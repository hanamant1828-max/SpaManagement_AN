"""
Professional Package Billing Integration Service
Handles automatic package benefit application with comprehensive tracking and audit
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload
from flask_login import current_user
from app import db
from models import (
    Customer, Service, ServicePackageAssignment, PackageBenefitTracker,
    PackageUsageHistory, EnhancedInvoice, InvoiceItem,
    PrepaidPackage, ServicePackage, Membership, StudentOffer, YearlyMembership
)
import logging

logger = logging.getLogger(__name__)

class PackageBillingService:
    """Professional package billing service with comprehensive benefit application"""

    # Priority order for package benefit application (lower number = higher priority)
    BENEFIT_PRIORITY = {
        'unlimited': 1,  # Membership unlimited access
        'free': 2,       # Free allocations with remaining count
        'discount': 3,   # Discount percentage
        'prepaid': 4     # Prepaid balance
    }

    @classmethod
    def get_customer_active_packages(cls, customer_id: int, service_date: datetime = None) -> List[PackageBenefitTracker]:
        """Get all active package benefits for a customer on a specific date"""
        if service_date is None:
            service_date = datetime.now()

        return PackageBenefitTracker.query.filter(
            and_(
                PackageBenefitTracker.customer_id == customer_id,
                PackageBenefitTracker.is_active == True,
                PackageBenefitTracker.valid_from <= service_date,
                PackageBenefitTracker.valid_to >= service_date
            )
        ).order_by(PackageBenefitTracker.benefit_type).all()

    @classmethod
    def find_applicable_packages(cls, customer_id: int, service_id: int, service_date: datetime = None) -> List[PackageBenefitTracker]:
        """Find all packages that can apply to a specific service"""
        if service_date is None:
            service_date = datetime.now()

        # Get active packages for customer
        active_packages = cls.get_customer_active_packages(customer_id, service_date)

        applicable_packages = []
        for package in active_packages:
            # Check if package covers this service
            if cls._package_covers_service(package, service_id):
                # Check if package has remaining benefits
                if cls._package_has_remaining_benefits(package):
                    applicable_packages.append(package)

        # Sort by priority
        applicable_packages.sort(key=lambda p: cls.BENEFIT_PRIORITY.get(p.benefit_type, 999))
        return applicable_packages

    @classmethod
    def _package_covers_service(cls, package: PackageBenefitTracker, service_id: int) -> bool:
        """Check if a package covers a specific service"""
        # Prepaid packages (credit-based) cover all services
        if package.benefit_type == 'prepaid' and package.service_id is None:
            return True

        # Direct service match for service packages
        if package.service_id == service_id:
            return True

        # For memberships - check if membership covers this service
        if package.benefit_type == 'unlimited':
            # If service_id is specified, it's only for that specific service
            if package.service_id is not None:
                return package.service_id == service_id
            
            # For memberships, ALWAYS check membership services (no unlimited access to all services)
            if package.package_assignment and package.package_assignment.package_type == 'membership':
                try:
                    from models import Membership, MembershipService
                    membership = Membership.query.get(package.package_assignment.package_reference_id)
                    if membership and hasattr(membership, 'membership_services'):
                        # Only return True if the service is specifically included in the membership
                        included_service_ids = [ms.service_id for ms in membership.membership_services]
                        print(f"DEBUG: Membership {membership.name} includes services: {included_service_ids}, checking service: {service_id}")
                        return service_id in included_service_ids
                    else:
                        print(f"DEBUG: Membership {membership.name if membership else 'None'} has no services configured")
                        return False
                except Exception as e:
                    print(f"Error checking membership services: {e}")
                    return False
            return False

        # Student offers and other discount types - check service assignments
        if package.benefit_type == 'discount':
            if package.service_id == service_id:
                return True
            # Check student offer services
            if package.package_assignment and package.package_assignment.package_type == 'student_offer':
                try:
                    from models import StudentOffer, StudentOfferService
                    offer = StudentOffer.query.get(package.package_assignment.package_reference_id)
                    if offer and hasattr(offer, 'student_offer_services'):
                        return any(sos.service_id == service_id for sos in offer.student_offer_services)
                except:
                    pass
            return False

        return False

    @classmethod
    def _package_has_remaining_benefits(cls, package: PackageBenefitTracker) -> bool:
        """Check if package has remaining benefits"""
        if package.benefit_type == 'unlimited':
            return True  # Unlimited always available during validity period

        if package.benefit_type == 'prepaid':
            return package.balance_remaining > 0

        if package.benefit_type in ['free', 'discount']:
            return package.remaining_count > 0

        return False

    @classmethod
    def apply_package_benefit(cls, customer_id: int, service_id: int, service_price: float,
                            invoice_id: int, invoice_item_id: int, service_date: datetime = None,
                            manual_package_id: int = None, requested_quantity: int = 1) -> Dict:
        """
        Apply package benefit to a service with comprehensive tracking

        Returns:
            {
                'success': bool,
                'applied': bool,
                'benefit_type': str,
                'original_price': float,
                'final_price': float,
                'deduction_amount': float,
                'package_name': str,
                'remaining_balance': dict,
                'usage_id': int,
                'message': str
            }
        """
        try:
            if service_date is None:
                service_date = datetime.now()

            # Create idempotency key
            idempotency_key = f"{invoice_id}_{invoice_item_id}"

            # Check if already processed
            existing_usage = PackageUsageHistory.query.filter_by(
                idempotency_key=idempotency_key
            ).first()

            if existing_usage:
                return {
                    'success': True,
                    'applied': True,
                    'message': 'Already processed (idempotent)',
                    'usage_id': existing_usage.id
                }

            # Find applicable packages
            if manual_package_id:
                # Staff manually selected a package
                applicable_package = PackageBenefitTracker.query.get(manual_package_id)
                # We need to check if the manually selected package covers the service
                if not applicable_package or not cls._package_covers_service(applicable_package, service_id):
                    return {
                        'success': False,
                        'applied': False,
                        'message': 'Manually selected package is not applicable to this service'
                    }
                applicable_packages = [applicable_package]
                staff_override = True
            else:
                # Automatic selection by priority
                applicable_packages = cls.find_applicable_packages(customer_id, service_id, service_date)
                staff_override = False

            if not applicable_packages:
                return {
                    'success': True,
                    'applied': False,
                    'original_price': service_price,
                    'final_price': service_price,
                    'deduction_amount': 0.0,
                    'message': 'No applicable packages found'
                }

            # Apply the highest priority package
            selected_package = applicable_packages[0]

            # Apply benefit based on type
            result = cls._apply_benefit_by_type(
                selected_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )

            if result['success']:
                db.session.commit()
                logger.info(f"Package benefit applied successfully: {result}")

            return result

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error applying package benefit: {str(e)}")
            return {
                'success': False,
                'applied': False,
                'message': f'Error applying package benefit: {str(e)}'
            }

    @classmethod
    def _apply_benefit_by_type(cls, package: PackageBenefitTracker, service_price: float,
                              customer_id: int, service_id: int, invoice_id: int,
                              invoice_item_id: int, idempotency_key: str,
                              service_date: datetime, staff_override: bool) -> Dict:
        """Apply benefit based on package type with concurrency control - SWITCH/CASE ROUTING"""

        # Lock the package record for update (concurrency control)
        locked_package = db.session.query(PackageBenefitTracker).filter_by(
            id=package.id
        ).with_for_update().first()

        if not locked_package:
            return {
                'success': False,
                'applied': False,
                'message': 'Package not found or locked'
            }

        # Re-check remaining benefits under lock
        if not cls._package_has_remaining_benefits(locked_package):
            return {
                'success': True,
                'applied': False,
                'original_price': service_price,
                'final_price': service_price,
                'deduction_amount': 0.0,
                'message': 'Package benefits exhausted'
            }

        # Get package type from assignment for routing (SWITCH/CASE LOGIC)
        package_type = locked_package.package_assignment.package_type if locked_package.package_assignment else None
        
        # SWITCH/CASE: Route to appropriate package type method
        if package_type == 'service_package':
            return cls._apply_service_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        elif package_type == 'prepaid':
            return cls._apply_prepaid_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        elif package_type == 'membership':
            return cls._apply_membership_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        elif package_type == 'student_offer':
            return cls._apply_student_offer_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        elif package_type == 'yearly_membership':
            return cls._apply_yearly_membership_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        elif package_type == 'kitty_party':
            return cls._apply_kitty_party_package_benefit(
                locked_package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        
        else:
            # Fallback to benefit_type routing for backward compatibility
            benefit_type = locked_package.benefit_type
            
            if benefit_type == 'unlimited':
                return cls._apply_unlimited_benefit(
                    locked_package, service_price, customer_id, service_id,
                    invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
                )
            elif benefit_type == 'free':
                return cls._apply_free_benefit(
                    locked_package, service_price, customer_id, service_id,
                    invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
                )
            elif benefit_type == 'discount':
                return cls._apply_discount_benefit(
                    locked_package, service_price, customer_id, service_id,
                    invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
                )
            elif benefit_type == 'prepaid':
                return cls._apply_prepaid_benefit(
                    locked_package, service_price, customer_id, service_id,
                    invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
                )
            else:
                return {
                    'success': False,
                    'applied': False,
                    'message': f'Unknown package type: {package_type} or benefit type: {benefit_type}'
                }

    @classmethod
    def _apply_unlimited_benefit(cls, package: PackageBenefitTracker, service_price: float,
                               customer_id: int, service_id: int, invoice_id: int,
                               invoice_item_id: int, idempotency_key: str,
                               service_date: datetime, staff_override: bool) -> Dict:
        """Apply unlimited membership benefit"""

        # Create usage record
        usage = PackageUsageHistory(
            customer_id=customer_id,
            package_benefit_id=package.id,
            invoice_id=invoice_id,
            invoice_item_id=invoice_item_id,
            service_id=service_id,
            idempotency_key=idempotency_key,
            benefit_type='unlimited',
            qty_deducted=1,
            amount_deducted=service_price,
            discount_applied=service_price,
            balance_after_qty=999999,  # Unlimited
            balance_after_amount=0.0,
            transaction_type='use',
            applied_rule='unlimited_membership',
            staff_override=staff_override,
            applied_by=current_user.id,
            charge_date=service_date,
            notes='Unlimited membership benefit applied'
        )

        db.session.add(usage)

        return {
            'success': True,
            'applied': True,
            'benefit_type': 'unlimited',
            'original_price': service_price,
            'final_price': 0.0,
            'deduction_amount': service_price,
            'package_name': cls._get_package_name(package),
            'remaining_balance': {'type': 'unlimited', 'message': 'Unlimited access'},
            'usage_id': usage.id,
            'message': 'Unlimited membership benefit applied'
        }

    @classmethod
    def _apply_free_benefit(cls, package: PackageBenefitTracker, service_price: float,
                          customer_id: int, service_id: int, invoice_id: int,
                          invoice_item_id: int, idempotency_key: str,
                          service_date: datetime, staff_override: bool) -> Dict:
        """Apply free session benefit with quantity awareness"""

        # Get the requested quantity from the invoice item
        from models import InvoiceItem
        invoice_item = InvoiceItem.query.get(invoice_item_id)
        requested_quantity = int(invoice_item.quantity) if invoice_item else 1

        # Validate that we have sessions remaining before applying
        if package.remaining_count <= 0:
            return {
                'success': True,
                'applied': False,
                'original_price': service_price,
                'final_price': service_price,
                'deduction_amount': 0.0,
                'message': f'No free sessions remaining in {cls._get_package_name(package)}'
            }

        # Calculate how many sessions can be covered by package
        sessions_to_cover = min(requested_quantity, package.remaining_count)
        sessions_to_pay = max(0, requested_quantity - sessions_to_cover)

        # Calculate pricing - ensure proper division
        if requested_quantity > 0:
            price_per_session = service_price / requested_quantity
        else:
            price_per_session = service_price

        covered_amount = sessions_to_cover * price_per_session
        final_price = sessions_to_pay * price_per_session

        # Ensure final price is never negative
        final_price = max(0, final_price)
        covered_amount = min(covered_amount, service_price)

        # Only deduct sessions if we're actually covering some
        if sessions_to_cover > 0:
            package.used_count += sessions_to_cover
            package.remaining_count = max(0, package.remaining_count - sessions_to_cover)

            # Auto-deactivate if exhausted
            if package.remaining_count == 0:
                package.is_active = False
            
            # CRITICAL: Sync with ServicePackageAssignment
            cls._sync_assignment_with_tracker(package)

        # Create usage record only if sessions were actually used
        if sessions_to_cover > 0:
            usage = PackageUsageHistory(
                customer_id=customer_id,
                package_benefit_id=package.id,
                invoice_id=invoice_id,
                invoice_item_id=invoice_item_id,
                service_id=service_id,
                idempotency_key=idempotency_key,
                benefit_type='free',
                qty_deducted=sessions_to_cover,
                amount_deducted=covered_amount,
                discount_applied=covered_amount,
                balance_after_qty=package.remaining_count,
                balance_after_amount=0.0,
                transaction_type='use',
                applied_rule='free_session_partial_coverage' if sessions_to_pay > 0 else 'free_session_full_coverage',
                staff_override=staff_override,
                applied_by=current_user.id,
                charge_date=service_date,
                notes=f'{sessions_to_cover} free sessions used. {sessions_to_pay} sessions charged. Remaining: {package.remaining_count}'
            )

            db.session.add(usage)
            usage_id = usage.id
        else:
            usage_id = None

        # Generate appropriate message
        if sessions_to_pay > 0 and sessions_to_cover > 0:
            # Partial coverage - some sessions free, some charged
            message = f'{sessions_to_cover} of {requested_quantity} sessions FREE via {cls._get_package_name(package)}, {sessions_to_pay} sessions charged (₹{final_price:.2f}). {package.remaining_count} free sessions remaining'
        elif sessions_to_cover == requested_quantity:
            # Full coverage - all sessions free
            message = f'All {sessions_to_cover} sessions FREE via {cls._get_package_name(package)}. {package.remaining_count} free sessions remaining'
        else:
            # No coverage - all sessions charged
            message = f'No free sessions available. All {requested_quantity} sessions charged (₹{service_price:.2f})'

        return {
            'success': True,
            'applied': sessions_to_cover > 0,
            'benefit_type': 'free',
            'original_price': service_price,
            'final_price': final_price,
            'deduction_amount': covered_amount,
            'package_name': cls._get_package_name(package),
            'sessions_covered': sessions_to_cover,
            'sessions_to_pay': sessions_to_pay,
            'remaining_balance': {
                'type': 'sessions',
                'remaining': package.remaining_count,
                'total': package.total_allocated
            },
            'usage_id': usage_id,
            'message': message
        }

    @classmethod
    def _apply_discount_benefit(cls, package: PackageBenefitTracker, service_price: float,
                              customer_id: int, service_id: int, invoice_id: int,
                              invoice_item_id: int, idempotency_key: str,
                              service_date: datetime, staff_override: bool) -> Dict:
        """Apply discount percentage benefit"""

        discount_amount = service_price * (package.discount_percentage / 100)
        final_price = service_price - discount_amount

        # Deduct from remaining count
        package.used_count += 1
        package.remaining_count = max(0, package.remaining_count - 1)

        # Auto-deactivate if exhausted
        if package.remaining_count == 0:
            package.is_active = False
        
        # CRITICAL: Sync with ServicePackageAssignment
        cls._sync_assignment_with_tracker(package)

        # Create usage record
        usage = PackageUsageHistory(
            customer_id=customer_id,
            package_benefit_id=package.id,
            invoice_id=invoice_id,
            invoice_item_id=invoice_item_id,
            service_id=service_id,
            idempotency_key=idempotency_key,
            benefit_type='discount',
            qty_deducted=1,
            amount_deducted=0.0,
            discount_applied=discount_amount,
            balance_after_qty=package.remaining_count,
            balance_after_amount=0.0,
            transaction_type='use',
            applied_rule='discount_percentage',
            staff_override=staff_override,
            applied_by=current_user.id,
            charge_date=service_date,
            notes=f'{package.discount_percentage}% discount applied. Remaining uses: {package.remaining_count}'
        )

        db.session.add(usage)

        return {
            'success': True,
            'applied': True,
            'benefit_type': 'discount',
            'original_price': service_price,
            'final_price': final_price,
            'deduction_amount': discount_amount,
            'package_name': cls._get_package_name(package),
            'remaining_balance': {
                'type': 'discount_uses',
                'remaining': package.remaining_count,
                'total': package.total_allocated,
                'discount_percent': package.discount_percentage
            },
            'usage_id': usage.id,
            'message': f'{package.discount_percentage}% discount applied. {package.remaining_count} uses remaining'
        }

    @classmethod
    def _apply_prepaid_benefit(cls, package: PackageBenefitTracker, service_price: float,
                             customer_id: int, service_id: int, invoice_id: int,
                             invoice_item_id: int, idempotency_key: str,
                             service_date: datetime, staff_override: bool) -> Dict:
        """Apply prepaid balance benefit with partial coverage support"""

        # Calculate deduction amount
        deduction_amount = min(service_price, package.balance_remaining)
        final_price = service_price - deduction_amount

        # Update package balances
        package.balance_used += deduction_amount
        package.balance_remaining = max(0, package.balance_remaining - deduction_amount)

        # Auto-deactivate if exhausted
        if package.balance_remaining == 0:
            package.is_active = False
        
        # CRITICAL: Sync with ServicePackageAssignment
        cls._sync_assignment_with_tracker(package)

        # Create usage record
        usage = PackageUsageHistory(
            customer_id=customer_id,
            package_benefit_id=package.id,
            invoice_id=invoice_id,
            invoice_item_id=invoice_item_id,
            service_id=service_id,
            idempotency_key=idempotency_key,
            benefit_type='prepaid',
            qty_deducted=0,
            amount_deducted=deduction_amount,
            discount_applied=deduction_amount,
            balance_after_qty=0,
            balance_after_amount=package.balance_remaining,
            transaction_type='use',
            applied_rule='prepaid_balance_deduction',
            staff_override=staff_override,
            applied_by=current_user.id,
            charge_date=service_date,
            notes=f'Prepaid deduction: ₹{deduction_amount}. Balance remaining: ₹{package.balance_remaining}'
        )

        db.session.add(usage)

        coverage_type = 'full' if final_price == 0 else 'partial'

        return {
            'success': True,
            'applied': True,
            'benefit_type': 'prepaid',
            'original_price': service_price,
            'final_price': final_price,
            'deduction_amount': deduction_amount,
            'package_name': cls._get_package_name(package),
            'remaining_balance': {
                'type': 'prepaid_balance',
                'remaining': package.balance_remaining,
                'total': package.balance_total
            },
            'usage_id': usage.id,
            'message': f'Prepaid {coverage_type} coverage: ₹{deduction_amount}. Balance: ₹{package.balance_remaining}'
        }

    @classmethod
    def _sync_assignment_with_tracker(cls, tracker: PackageBenefitTracker):
        """
        CRITICAL: Sync ServicePackageAssignment with PackageBenefitTracker
        This ensures data consistency between the two tracking systems
        """
        try:
            assignment = tracker.package_assignment
            if not assignment:
                logger.warning(f"PackageBenefitTracker {tracker.id} has no assignment - cannot sync")
                return
            
            # Sync session-based packages
            if tracker.benefit_type in ['free', 'discount']:
                assignment.total_sessions = tracker.total_allocated or 0
                assignment.used_sessions = tracker.used_count or 0
                assignment.remaining_sessions = tracker.remaining_count or 0
                
                # Update status if package is exhausted
                if tracker.remaining_count <= 0 and assignment.status == 'active':
                    assignment.status = 'completed'
            
            # Sync prepaid packages
            elif tracker.benefit_type == 'prepaid':
                assignment.credit_amount = tracker.balance_total or 0
                assignment.used_credit = tracker.balance_used or 0
                assignment.remaining_credit = tracker.balance_remaining or 0
                
                # Update status if credit is exhausted
                if tracker.balance_remaining <= 0 and assignment.status == 'active':
                    assignment.status = 'completed'
            
            # Check expiry
            if assignment.expires_on and assignment.expires_on < datetime.now():
                if assignment.status == 'active':
                    assignment.status = 'expired'
                if tracker.is_active:
                    tracker.is_active = False
            
            logger.info(f"✅ Synced assignment {assignment.id} with tracker {tracker.id}")
            
        except Exception as e:
            logger.error(f"Error syncing assignment with tracker: {str(e)}")

    @classmethod
    def _get_package_name(cls, package: PackageBenefitTracker) -> str:
        """Get package name from assignment"""
        try:
            template = package.package_assignment.get_package_template()
            return template.name if template else 'Unknown Package'
        except:
            return 'Package'

    @classmethod
    def reverse_package_usage(cls, usage_id: int, reason: str = 'refund') -> Dict:
        """Reverse a package usage (for refunds/voids)"""
        try:
            usage = PackageUsageHistory.query.get(usage_id)
            if not usage:
                return {'success': False, 'message': 'Usage record not found'}

            # Check if already reversed
            if usage.transaction_type in ['refund', 'void']:
                return {'success': False, 'message': 'Usage already reversed'}

            # Get and lock the package
            package = db.session.query(PackageBenefitTracker).filter_by(
                id=usage.package_benefit_id
            ).with_for_update().first()

            if not package:
                return {'success': False, 'message': 'Package not found'}

            # Restore benefits based on type
            if usage.benefit_type in ['free', 'discount']:
                package.used_count = max(0, package.used_count - usage.qty_deducted)
                package.remaining_count += usage.qty_deducted
                package.is_active = True  # Reactivate if was exhausted

            elif usage.benefit_type == 'prepaid':
                package.balance_used = max(0, package.balance_used - usage.amount_deducted)
                package.balance_remaining += usage.amount_deducted
                package.is_active = True  # Reactivate if was exhausted

            # Create reversal record
            reversal = PackageUsageHistory(
                customer_id=usage.customer_id,
                package_benefit_id=usage.package_benefit_id,
                invoice_id=usage.invoice_id,
                invoice_item_id=usage.invoice_item_id,
                service_id=usage.service_id,
                idempotency_key=f"{usage.idempotency_key}_reversal_{datetime.now().timestamp()}",
                benefit_type=usage.benefit_type,
                qty_deducted=-usage.qty_deducted,  # Negative for reversal
                amount_deducted=-usage.amount_deducted,  # Negative for reversal
                discount_applied=-usage.discount_applied,
                balance_after_qty=package.remaining_count,
                balance_after_amount=package.balance_remaining,
                transaction_type=reason,
                reversal_reference_id=usage.id,
                applied_rule=f'reversal_{reason}',
                staff_override=True,
                applied_by=current_user.id,
                charge_date=datetime.now(),
                notes=f'Reversal of usage {usage.id}. Reason: {reason}'
            )

            db.session.add(reversal)
            db.session.commit()

            return {
                'success': True,
                'message': f'Usage reversed successfully. Benefits restored.',
                'reversal_id': reversal.id
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reversing package usage: {str(e)}")
            return {'success': False, 'message': f'Error reversing usage: {str(e)}'}

    @classmethod
    def _apply_service_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                      customer_id: int, service_id: int, invoice_id: int,
                                      invoice_item_id: int, idempotency_key: str,
                                      service_date: datetime, staff_override: bool) -> Dict:
        """Apply SERVICE PACKAGE benefit - tracks sessions and applies free sessions"""
        logger.info(f"SERVICE PACKAGE: Applying benefit for package {package.id}")
        
        # Service packages use free sessions benefit
        return cls._apply_free_benefit(
            package, service_price, customer_id, service_id,
            invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
        )
    
    @classmethod
    def _apply_prepaid_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                      customer_id: int, service_id: int, invoice_id: int,
                                      invoice_item_id: int, idempotency_key: str,
                                      service_date: datetime, staff_override: bool) -> Dict:
        """Apply PREPAID PACKAGE benefit - deducts from credit balance"""
        logger.info(f"PREPAID PACKAGE: Applying benefit for package {package.id}")
        
        # Prepaid packages use balance deduction
        return cls._apply_prepaid_benefit(
            package, service_price, customer_id, service_id,
            invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
        )
    
    @classmethod
    def _apply_membership_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                         customer_id: int, service_id: int, invoice_id: int,
                                         invoice_item_id: int, idempotency_key: str,
                                         service_date: datetime, staff_override: bool) -> Dict:
        """Apply MEMBERSHIP PACKAGE benefit - provides unlimited access to included services"""
        logger.info(f"MEMBERSHIP PACKAGE: Applying benefit for package {package.id}")
        
        # Memberships use unlimited benefit
        return cls._apply_unlimited_benefit(
            package, service_price, customer_id, service_id,
            invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
        )
    
    @classmethod
    def _apply_student_offer_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                            customer_id: int, service_id: int, invoice_id: int,
                                            invoice_item_id: int, idempotency_key: str,
                                            service_date: datetime, staff_override: bool) -> Dict:
        """Apply STUDENT OFFER PACKAGE benefit - applies discount percentage"""
        logger.info(f"STUDENT OFFER PACKAGE: Applying benefit for package {package.id}")
        
        # Student offers use discount benefit
        return cls._apply_discount_benefit(
            package, service_price, customer_id, service_id,
            invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
        )
    
    @classmethod
    def _apply_yearly_membership_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                                customer_id: int, service_id: int, invoice_id: int,
                                                invoice_item_id: int, idempotency_key: str,
                                                service_date: datetime, staff_override: bool) -> Dict:
        """Apply YEARLY MEMBERSHIP PACKAGE benefit - provides unlimited access for a year"""
        logger.info(f"YEARLY MEMBERSHIP PACKAGE: Applying benefit for package {package.id}")
        
        # Yearly memberships use unlimited benefit
        return cls._apply_unlimited_benefit(
            package, service_price, customer_id, service_id,
            invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
        )
    
    @classmethod
    def _apply_kitty_party_package_benefit(cls, package: PackageBenefitTracker, service_price: float,
                                          customer_id: int, service_id: int, invoice_id: int,
                                          invoice_item_id: int, idempotency_key: str,
                                          service_date: datetime, staff_override: bool) -> Dict:
        """Apply KITTY PARTY PACKAGE benefit - special group package with session tracking"""
        logger.info(f"KITTY PARTY PACKAGE: Applying benefit for package {package.id}")
        
        # Kitty party packages can use either free sessions or discount based on configuration
        if package.benefit_type == 'free':
            return cls._apply_free_benefit(
                package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )
        else:
            return cls._apply_discount_benefit(
                package, service_price, customer_id, service_id,
                invoice_id, invoice_item_id, idempotency_key, service_date, staff_override
            )

    @classmethod
    def get_customer_package_summary(cls, customer_id: int) -> Dict:
        """Get comprehensive package summary for customer profile"""
        try:
            active_packages = cls.get_customer_active_packages(customer_id)

            summary = {
                'total_active_packages': len(active_packages),
                'packages': []
            }

            for package in active_packages:
                package_info = {
                    'id': package.id,
                    'name': cls._get_package_name(package),
                    'benefit_type': package.benefit_type,
                    'valid_from': package.valid_from.strftime('%Y-%m-%d'),
                    'valid_to': package.valid_to.strftime('%Y-%m-%d'),
                    'is_active': package.is_active,
                    'service_name': package.service.name if package.service else 'All Services'
                }

                # Add type-specific details
                if package.benefit_type in ['free', 'discount']:
                    package_info.update({
                        'total_allocated': package.total_allocated,
                        'used_count': package.used_count,
                        'remaining_count': package.remaining_count,
                        'usage_percentage': round((package.used_count / package.total_allocated) * 100, 1) if package.total_allocated > 0 else 0
                    })

                    if package.benefit_type == 'discount':
                        package_info['discount_percentage'] = package.discount_percentage

                elif package.benefit_type == 'prepaid':
                    package_info.update({
                        'balance_total': package.balance_total,
                        'balance_used': package.balance_used,
                        'balance_remaining': package.balance_remaining,
                        'usage_percentage': round((package.balance_used / package.balance_total) * 100, 1) if package.balance_total > 0 else 0
                    })

                elif package.benefit_type == 'unlimited':
                    package_info.update({
                        'access_type': 'unlimited',
                        'usage_percentage': 0  # N/A for unlimited
                    })

                summary['packages'].append(package_info)

            return summary

        except Exception as e:
            logger.error(f"Error getting customer package summary: {str(e)}")
            return {'total_active_packages': 0, 'packages': []}