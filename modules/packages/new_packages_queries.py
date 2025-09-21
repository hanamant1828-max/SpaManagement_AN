"""
New Package Management Queries - Separate CRUD for each package type
"""
from app import db
from datetime import datetime
from sqlalchemy import and_, or_

# Import models from the main models file to avoid duplication
from models import (
    PrepaidPackage, ServicePackage, Membership,
    StudentOffer, YearlyMembership, KittyParty,
    Service, StudentOfferService
)

# ========================================
# STATISTICS AND OVERVIEW
# ========================================

def get_all_package_statistics():
    """Get statistics for all package types"""
    stats = {
        'prepaid_packages': PrepaidPackage.query.filter_by(is_active=True).count(),
        'service_packages': ServicePackage.query.filter_by(is_active=True).count(),
        'memberships': Membership.query.filter_by(is_active=True).count(),
        'student_offers': StudentOffer.query.filter_by(is_active=True).count(),
        'yearly_memberships': YearlyMembership.query.filter_by(is_active=True).count(),
        'kitty_parties': KittyParty.query.filter_by(is_active=True).count(),
    }

    # Calculate total packages
    stats['total_packages'] = sum(stats.values())

    return stats

# ========================================
# PREPAID PACKAGES CRUD
# ========================================

def get_all_prepaid_packages():
    """Get all active prepaid packages"""
    return PrepaidPackage.query.filter_by(is_active=True).order_by(PrepaidPackage.name).all()

def get_prepaid_package_by_id(package_id):
    """Get prepaid package by ID"""
    return PrepaidPackage.query.get(package_id)

def create_prepaid_package(data):
    """Create new prepaid package"""
    package = PrepaidPackage(
        name=data['name'],
        actual_price=float(data['actual_price']),
        after_value=float(data['after_value']),
        benefit_percent=float(data['benefit_percent']),
        validity_months=int(data['validity_months']),
        is_active=data.get('is_active', True)
    )
    db.session.add(package)
    db.session.commit()
    return package

def update_prepaid_package(package_id, data):
    """Update prepaid package"""
    package = PrepaidPackage.query.get(package_id)
    if not package:
        raise ValueError("Prepaid package not found")

    package.name = data['name']
    package.actual_price = float(data['actual_price'])
    package.after_value = float(data['after_value'])
    package.benefit_percent = float(data['benefit_percent'])
    package.validity_months = int(data['validity_months'])
    package.is_active = data.get('is_active', True)

    db.session.commit()
    return package

def delete_prepaid_package(package_id):
    """Delete prepaid package"""
    package = PrepaidPackage.query.get(package_id)
    if not package:
        raise ValueError("Prepaid package not found")

    package.is_active = False
    db.session.commit()
    return True

# ========================================
# SERVICE PACKAGES CRUD
# ========================================

def get_all_service_packages():
    """Get all active service packages"""
    return ServicePackage.query.filter_by(is_active=True).order_by(ServicePackage.name).all()

def get_service_package_by_id(package_id):
    """Get service package by ID"""
    return ServicePackage.query.get(package_id)

def create_service_package(data):
    """Create new service package"""
    package = ServicePackage(
        name=data['name'],
        service_id=int(data['service_id']) if data.get('service_id') else None,
        pay_for=int(data['pay_for']),
        total_services=int(data['total_services']),
        benefit_percent=float(data['benefit_percent']),
        validity_months=int(data.get('validity_months')) if data.get('validity_months') else None,
        is_active=data.get('is_active', True)
    )
    db.session.add(package)
    db.session.commit()
    return package

def update_service_package(package_id, data):
    """Update service package"""
    package = ServicePackage.query.get(package_id)
    if not package:
        raise ValueError("Service package not found")

    package.name = data['name']
    package.service_id = int(data['service_id']) if data.get('service_id') else None
    package.pay_for = int(data['pay_for'])
    package.total_services = int(data['total_services'])
    package.benefit_percent = float(data['benefit_percent'])
    package.validity_months = int(data.get('validity_months')) if data.get('validity_months') else None
    package.is_active = data.get('is_active', True)

    db.session.commit()
    return package

def delete_service_package(package_id):
    """Delete service package"""
    package = ServicePackage.query.get(package_id)
    if not package:
        raise ValueError("Service package not found")

    package.is_active = False
    db.session.commit()
    return True

# ========================================
# MEMBERSHIPS CRUD
# ========================================

def get_all_memberships():
    """Get all active memberships"""
    return Membership.query.filter_by(is_active=True).order_by(Membership.name).all()

def get_membership_by_id(membership_id):
    """Get membership by ID"""
    return Membership.query.get(membership_id)

def create_membership(data):
    """Create new membership"""
    membership = Membership(
        name=data['name'],
        price=float(data['price']),
        validity_months=int(data['validity_months']),
        services_included=data.get('services_included', ''),  # Keep for backward compatibility
        is_active=data.get('is_active', True)
    )
    db.session.add(membership)
    db.session.flush()  # Get the membership ID

    # Add selected services
    if 'service_ids' in data and data['service_ids']:
        from models import MembershipService
        service_ids = data['service_ids'] if isinstance(data['service_ids'], list) else [data['service_ids']]
        for service_id in service_ids:
            if service_id:  # Skip empty values
                membership_service = MembershipService(
                    membership_id=membership.id,
                    service_id=int(service_id)
                )
                db.session.add(membership_service)

    db.session.commit()
    return membership

def update_membership(membership_id, data):
    """Update membership"""
    membership = Membership.query.get(membership_id)
    if not membership:
        raise ValueError("Membership not found")

    membership.name = data['name']
    membership.price = float(data['price'])
    membership.validity_months = int(data['validity_months'])
    membership.services_included = data.get('services_included', '')
    membership.is_active = data.get('is_active', True)

    # Update service relationships
    from models import MembershipService
    # Remove existing services
    MembershipService.query.filter_by(membership_id=membership_id).delete()

    # Add new services
    if 'service_ids' in data and data['service_ids']:
        service_ids = data['service_ids'] if isinstance(data['service_ids'], list) else [data['service_ids']]
        for service_id in service_ids:
            if service_id:  # Skip empty values
                membership_service = MembershipService(
                    membership_id=membership_id,
                    service_id=int(service_id)
                )
                db.session.add(membership_service)

    db.session.commit()
    return membership

def delete_membership(membership_id):
    """Delete membership"""
    membership = Membership.query.get(membership_id)
    if not membership:
        raise ValueError("Membership not found")

    membership.is_active = False
    db.session.commit()
    return True

# ========================================
# STUDENT OFFERS CRUD
# ========================================

def get_all_student_offers():
    """Get all student offers"""
    from models import StudentOffer
    return StudentOffer.query.filter_by(is_active=True).order_by(StudentOffer.created_at.desc()).all()

def get_student_offer_by_id(offer_id):
    """Get student offer by ID"""
    from models import StudentOffer
    return StudentOffer.query.get(offer_id)

def create_student_offer(data):
    """Create new student offer"""
    from models import StudentOffer, StudentOfferService
    from app import db

    offer = StudentOffer(
        discount_percentage=float(data['discount_percentage']),
        valid_from=datetime.strptime(data['valid_from'], '%Y-%m-%d').date(),
        valid_to=datetime.strptime(data['valid_to'], '%Y-%m-%d').date(),
        valid_days=data.get('valid_days', 'Mon-Fri'),
        conditions=data.get('conditions', 'Valid with Student ID'),
        is_active=bool(data.get('is_active', True))
    )

    db.session.add(offer)
    db.session.flush()  # Get the offer ID

    # Add service mappings
    service_ids = data.get('service_ids', [])
    if isinstance(service_ids, str):
        service_ids = [service_ids]

    for service_id in service_ids:
        if service_id:
            offer_service = StudentOfferService(
                offer_id=offer.id,
                service_id=int(service_id)
            )
            db.session.add(offer_service)

    db.session.commit()
    return offer

def update_student_offer(offer_id, data):
    """Update student offer"""
    from models import StudentOffer, StudentOfferService
    from app import db

    offer = StudentOffer.query.get_or_404(offer_id)

    offer.discount_percentage = float(data['discount_percentage'])
    offer.valid_from = datetime.strptime(data['valid_from'], '%Y-%m-%d').date()
    offer.valid_to = datetime.strptime(data['valid_to'], '%Y-%m-%d').date()
    offer.valid_days = data.get('valid_days', 'Mon-Fri')
    offer.conditions = data.get('conditions', 'Valid with Student ID')
    offer.is_active = bool(data.get('is_active', True))

    # Update service mappings
    # First, remove existing mappings
    StudentOfferService.query.filter_by(offer_id=offer.id).delete()

    # Add new mappings
    service_ids = data.get('service_ids', [])
    if isinstance(service_ids, str):
        service_ids = [service_ids]

    for service_id in service_ids:
        if service_id:
            offer_service = StudentOfferService(
                offer_id=offer.id,
                service_id=int(service_id)
            )
            db.session.add(offer_service)

    db.session.commit()
    return offer

def delete_student_offer(offer_id):
    """Delete student offer"""
    offer = StudentOffer.query.get(offer_id)
    if not offer:
        raise ValueError("Student offer not found")

    offer.is_active = False
    db.session.commit()
    return True

# ========================================
# YEARLY MEMBERSHIPS CRUD
# ========================================

def get_all_yearly_memberships():
    """Get all active yearly memberships"""
    return YearlyMembership.query.filter_by(is_active=True).order_by(YearlyMembership.name).all()

def get_yearly_membership_by_id(membership_id):
    """Get yearly membership by ID"""
    return YearlyMembership.query.get(membership_id)

def create_yearly_membership(data):
    """Create new yearly membership"""
    membership = YearlyMembership(
        name=data['name'],
        price=float(data['price']),
        discount_percent=float(data['discount_percent']),
        validity_months=int(data.get('validity_months', 12)),
        extra_benefits=data.get('extra_benefits'),
        is_active=data.get('is_active', True)
    )
    db.session.add(membership)
    db.session.commit()
    return membership

def update_yearly_membership(membership_id, data):
    """Update yearly membership"""
    membership = YearlyMembership.query.get(membership_id)
    if not membership:
        raise ValueError("Yearly membership not found")

    membership.name = data['name']
    membership.price = float(data['price'])
    membership.discount_percent = float(data['discount_percent'])
    membership.validity_months = int(data.get('validity_months', 12))
    membership.extra_benefits = data.get('extra_benefits')
    membership.is_active = data.get('is_active', True)

    db.session.commit()
    return membership

def delete_yearly_membership(membership_id):
    """Delete yearly membership"""
    membership = YearlyMembership.query.get(membership_id)
    if not membership:
        raise ValueError("Yearly membership not found")

    membership.is_active = False
    db.session.commit()
    return True

# ========================================
# KITTY PARTIES CRUD
# ========================================

def get_all_kitty_parties():
    """Get all kitty parties with linked services"""
    from sqlalchemy.orm import joinedload
    return KittyParty.query.options(
        joinedload(KittyParty.kittyparty_services).joinedload('service')
    ).filter_by(is_active=True).order_by(KittyParty.created_at.desc()).all()

def get_kitty_party_by_id(party_id):
    """Get kitty party by ID"""
    return KittyParty.query.get(party_id)

def create_kitty_party(data):
    """Create new kitty party"""
    party = KittyParty(
        name=data['name'],
        price=float(data['price']),
        after_value=float(data.get('after_value')) if data.get('after_value') else None,
        min_guests=int(data['min_guests']),
        services_included='',  # This field will be populated by KittyPartyService
        is_active=data.get('is_active', True)
    )
    db.session.add(party)
    db.session.flush()  # Get the party ID

    # Add selected services
    if 'service_ids' in data and data['service_ids']:
        from models import KittyPartyService
        service_ids = data['service_ids'] if isinstance(data['service_ids'], list) else [data['service_ids']]
        for service_id in service_ids:
            if service_id:  # Skip empty values
                kittyparty_service = KittyPartyService(
                    kittyparty_id=party.id,
                    service_id=int(service_id)
                )
                db.session.add(kittyparty_service)

    db.session.commit()
    return party

def update_kitty_party(party_id, data):
    """Update existing kitty party"""
    party = KittyParty.query.get(party_id)
    if not party:
        raise ValueError("Kitty party not found")

    # Update basic fields
    party.name = data['name']
    party.price = float(data['price'])
    party.after_value = float(data.get('after_value')) if data.get('after_value') else None
    party.min_guests = int(data['min_guests'])
    party.is_active = data.get('is_active', True)

    # Update services - remove existing and add new ones
    from models import KittyPartyService
    # Remove existing service relationships
    KittyPartyService.query.filter_by(kittyparty_id=party_id).delete()

    # Add new service relationships
    if 'service_ids' in data and data['service_ids']:
        service_ids = data['service_ids'] if isinstance(data['service_ids'], list) else [data['service_ids']]
        for service_id in service_ids:
            if service_id:  # Skip empty values
                kittyparty_service = KittyPartyService(
                    kittyparty_id=party_id,
                    service_id=int(service_id)
                )
                db.session.add(kittyparty_service)

    db.session.commit()
    return party

def delete_kitty_party(party_id):
    """Delete kitty party"""
    party = KittyParty.query.get(party_id)
    if not party:
        raise ValueError("Kitty party not found")

    party.is_active = False
    db.session.commit()
    return True

# Note: get_all_package_statistics function is already defined above