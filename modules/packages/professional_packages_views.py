"""
Professional Packages Management Views
Enhanced package management with comprehensive billing integration
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc

# Import models
from models import (
    Customer, Service, ServicePackageAssignment, PackageBenefitTracker, 
    PackageUsageHistory, PrepaidPackage, ServicePackage, Membership, 
    StudentOffer, YearlyMembership, KittyParty
)

# Import our new billing service
from .package_billing_service import PackageBillingService

@app.route('/professional-packages')
@login_required
def professional_packages():
    """Main professional packages management interface"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get comprehensive statistics aligned with template expectations
    total_packages = (PrepaidPackage.query.filter_by(is_active=True).count() +
                     ServicePackage.query.filter_by(is_active=True).count() +
                     Membership.query.filter_by(is_active=True).count() +
                     StudentOffer.query.filter_by(is_active=True).count() +
                     YearlyMembership.query.filter_by(is_active=True).count() +
                     KittyParty.query.filter_by(is_active=True).count())
    
    stats = {
        'total_packages': total_packages,
        'prepaid_credit_packages': PrepaidPackage.query.filter_by(is_active=True).count(),
        'prepaid_service_packages': ServicePackage.query.filter_by(is_active=True).count(),
        'membership_packages': Membership.query.filter_by(is_active=True).count(),
        'regular_packages': StudentOffer.query.filter_by(is_active=True).count(),
        'client_assignments': ServicePackageAssignment.query.filter_by(status='active').count(),
        # Additional useful stats
        'total_active_packages': PackageBenefitTracker.query.filter_by(is_active=True).count(),
        'total_customers_with_packages': db.session.query(PackageBenefitTracker.customer_id).distinct().count(),
        'total_prepaid_balance': db.session.query(
            db.func.sum(PackageBenefitTracker.balance_remaining)
        ).filter_by(benefit_type='prepaid', is_active=True).scalar() or 0,
        'total_free_sessions_remaining': db.session.query(
            db.func.sum(PackageBenefitTracker.remaining_count)
        ).filter_by(benefit_type='free', is_active=True).scalar() or 0,
        'total_usage_today': PackageUsageHistory.query.filter(
            db.func.date(PackageUsageHistory.charge_date) == datetime.now().date()
        ).count()
    }
    
    # Get recent package activities
    recent_activities = PackageUsageHistory.query.options(
        db.joinedload(PackageUsageHistory.customer),
        db.joinedload(PackageUsageHistory.service),
        db.joinedload(PackageUsageHistory.applied_by_user)
    ).order_by(desc(PackageUsageHistory.created_at)).limit(10).all()
    
    # Get customers for assignment
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.full_name).all()
    
    # Get services for package creation
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    
    # Get all package templates
    prepaid_packages = PrepaidPackage.query.filter_by(is_active=True).all()
    service_packages = ServicePackage.query.filter_by(is_active=True).all()
    memberships = Membership.query.filter_by(is_active=True).all()
    student_offers = StudentOffer.query.filter_by(is_active=True).all()
    yearly_memberships = YearlyMembership.query.filter_by(is_active=True).all()
    kitty_parties = KittyParty.query.filter_by(is_active=True).all()
    
    return render_template('professional_packages.html',
                         stats=stats,
                         recent_activities=recent_activities,
                         customers=customers,
                         services=services,
                         prepaid_packages=prepaid_packages,
                         service_packages=service_packages,
                         memberships=memberships,
                         student_offers=student_offers,
                         yearly_memberships=yearly_memberships,
                         kitty_parties=kitty_parties)

@app.route('/api/professional-packages/assign', methods=['POST'])
@login_required
def api_assign_professional_package():
    """Assign a package to customer with comprehensive benefit tracking"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'package_type', 'package_id', 'validity_months']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        customer_id = int(data['customer_id'])
        package_type = data['package_type']
        package_id = int(data['package_id'])
        validity_months = int(data['validity_months'])
        
        # Get customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 400
        
        # Get package template
        package_template = None
        if package_type == 'prepaid':
            package_template = PrepaidPackage.query.get(package_id)
        elif package_type == 'service_package':
            package_template = ServicePackage.query.get(package_id)
        elif package_type == 'membership':
            package_template = Membership.query.get(package_id)
        elif package_type == 'student_offer':
            package_template = StudentOffer.query.get(package_id)
        elif package_type == 'yearly_membership':
            package_template = YearlyMembership.query.get(package_id)
        elif package_type == 'kitty_party':
            package_template = KittyParty.query.get(package_id)
        
        if not package_template:
            return jsonify({'success': False, 'message': 'Package template not found'}), 400
        
        # Calculate dates
        assigned_on = datetime.now()
        expires_on = assigned_on + timedelta(days=validity_months * 30)
        
        # Create package assignment
        assignment = ServicePackageAssignment(
            customer_id=customer_id,
            package_type=package_type,
            package_reference_id=package_id,
            assigned_on=assigned_on,
            expires_on=expires_on,
            price_paid=float(data.get('price_paid', package_template.price if hasattr(package_template, 'price') else 0)),
            discount=float(data.get('discount', 0)),
            status='active',
            notes=data.get('notes', '')
        )
        
        # Set package-specific fields
        if package_type == 'prepaid':
            assignment.credit_amount = package_template.after_value
            assignment.remaining_credit = package_template.after_value
        elif package_type in ['service_package', 'student_offer']:
            assignment.total_sessions = data.get('total_sessions', 1)
            assignment.remaining_sessions = assignment.total_sessions
        
        db.session.add(assignment)
        db.session.flush()  # Get assignment ID
        
        # Create benefit trackers based on package type
        benefit_trackers = []
        
        if package_type == 'prepaid':
            # Prepaid package - covers all services
            tracker = PackageBenefitTracker(
                customer_id=customer_id,
                package_assignment_id=assignment.id,
                service_id=None,  # NULL for prepaid (covers all services)
                benefit_type='prepaid',
                balance_total=package_template.after_value,
                balance_remaining=package_template.after_value,
                valid_from=assigned_on,
                valid_to=expires_on
            )
            benefit_trackers.append(tracker)
            
        elif package_type == 'membership':
            # Membership - unlimited access to included services
            if hasattr(package_template, 'services_included') and package_template.services_included:
                # Parse services included (comma-separated IDs)
                try:
                    service_ids = [int(sid.strip()) for sid in package_template.services_included.split(',') if sid.strip()]
                    for service_id in service_ids:
                        tracker = PackageBenefitTracker(
                            customer_id=customer_id,
                            package_assignment_id=assignment.id,
                            service_id=service_id,
                            benefit_type='unlimited',
                            valid_from=assigned_on,
                            valid_to=expires_on
                        )
                        benefit_trackers.append(tracker)
                except:
                    # If parsing fails, create unlimited for all services
                    tracker = PackageBenefitTracker(
                        customer_id=customer_id,
                        package_assignment_id=assignment.id,
                        service_id=None,
                        benefit_type='unlimited',
                        valid_from=assigned_on,
                        valid_to=expires_on
                    )
                    benefit_trackers.append(tracker)
            else:
                # Unlimited access to all services
                tracker = PackageBenefitTracker(
                    customer_id=customer_id,
                    package_assignment_id=assignment.id,
                    service_id=None,
                    benefit_type='unlimited',
                    valid_from=assigned_on,
                    valid_to=expires_on
                )
                benefit_trackers.append(tracker)
                
        elif package_type == 'service_package':
            # Service package - free sessions for specific service
            tracker = PackageBenefitTracker(
                customer_id=customer_id,
                package_assignment_id=assignment.id,
                service_id=package_template.service_id,
                benefit_type='free',
                total_allocated=assignment.total_sessions,
                remaining_count=assignment.total_sessions,
                valid_from=assigned_on,
                valid_to=expires_on
            )
            benefit_trackers.append(tracker)
            
        elif package_type == 'student_offer':
            # Student offer - discount on specific services
            if hasattr(package_template, 'services') and package_template.services:
                for service_relation in package_template.services:
                    tracker = PackageBenefitTracker(
                        customer_id=customer_id,
                        package_assignment_id=assignment.id,
                        service_id=service_relation.service_id,
                        benefit_type='discount',
                        discount_percentage=package_template.discount_percent,
                        total_allocated=data.get('total_uses', 10),  # Default 10 uses
                        remaining_count=data.get('total_uses', 10),
                        valid_from=assigned_on,
                        valid_to=expires_on
                    )
                    benefit_trackers.append(tracker)
        
        # Add all benefit trackers
        for tracker in benefit_trackers:
            db.session.add(tracker)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Package assigned successfully to {customer.full_name}',
            'assignment_id': assignment.id,
            'benefit_trackers_created': len(benefit_trackers)
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error assigning package: {str(e)}")
        return jsonify({'success': False, 'message': f'Error assigning package: {str(e)}'}), 500

@app.route('/api/professional-packages/customer/<int:customer_id>/summary')
@login_required
def api_customer_package_summary(customer_id):
    """Get comprehensive package summary for a customer"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        summary = PackageBillingService.get_customer_package_summary(customer_id)
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        app.logger.error(f"Error getting customer package summary: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/professional-packages/customer/<int:customer_id>/applicable/<int:service_id>')
@login_required
def api_customer_applicable_packages(customer_id, service_id):
    """Get applicable packages for a customer and service (for billing integration)"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        applicable_packages = PackageBillingService.find_applicable_packages(customer_id, service_id)
        
        packages_data = []
        for package in applicable_packages:
            package_info = {
                'id': package.id,
                'name': PackageBillingService._get_package_name(package),
                'benefit_type': package.benefit_type,
                'priority': PackageBillingService.BENEFIT_PRIORITY.get(package.benefit_type, 999)
            }
            
            # Add type-specific details
            if package.benefit_type == 'unlimited':
                package_info['description'] = 'Unlimited access'
            elif package.benefit_type == 'free':
                package_info['description'] = f'{package.remaining_count} free sessions remaining'
            elif package.benefit_type == 'discount':
                package_info['description'] = f'{package.discount_percentage}% discount ({package.remaining_count} uses remaining)'
            elif package.benefit_type == 'prepaid':
                package_info['description'] = f'₹{package.balance_remaining} prepaid balance'
            
            packages_data.append(package_info)
        
        return jsonify({
            'success': True,
            'applicable_packages': packages_data
        })
        
    except Exception as e:
        app.logger.error(f"Error getting applicable packages: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/professional-packages/usage/reverse/<int:usage_id>', methods=['POST'])
@login_required
def api_reverse_package_usage(usage_id):
    """Reverse package usage (for refunds/voids)"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'refund')
        
        result = PackageBillingService.reverse_package_usage(usage_id, reason)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error reversing package usage: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/professional-packages/analytics')
@login_required
def professional_packages_analytics():
    """Professional packages analytics and reporting"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Monthly usage analytics
        from sqlalchemy import extract
        
        current_year = datetime.now().year
        monthly_usage = db.session.query(
            extract('month', PackageUsageHistory.charge_date).label('month'),
            db.func.count(PackageUsageHistory.id).label('total_usage'),
            db.func.sum(PackageUsageHistory.amount_deducted).label('total_deductions')
        ).filter(
            extract('year', PackageUsageHistory.charge_date) == current_year
        ).group_by(extract('month', PackageUsageHistory.charge_date)).all()
        
        # Top customers by package usage
        top_customers = db.session.query(
            Customer.full_name,
            db.func.count(PackageUsageHistory.id).label('usage_count'),
            db.func.sum(PackageUsageHistory.amount_deducted).label('total_savings')
        ).join(PackageUsageHistory).group_by(
            Customer.id, Customer.full_name
        ).order_by(desc('usage_count')).limit(10).all()
        
        # Package performance
        package_performance = db.session.query(
            PackageBenefitTracker.benefit_type,
            db.func.count(PackageBenefitTracker.id).label('total_packages'),
            db.func.count(PackageUsageHistory.id).label('total_usage')
        ).outerjoin(PackageUsageHistory).group_by(
            PackageBenefitTracker.benefit_type
        ).all()
        
        return render_template('professional_packages_analytics.html',
                             monthly_usage=monthly_usage,
                             top_customers=top_customers,
                             package_performance=package_performance,
                             current_year=current_year)
        
    except Exception as e:
        app.logger.error(f"Error loading package analytics: {str(e)}")
        flash('Error loading analytics', 'danger')
        return redirect(url_for('professional_packages'))