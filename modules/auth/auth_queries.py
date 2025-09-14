"""
Authentication-related database queries
"""

def get_user_by_username(username):
    """Get user by username"""
    from models import User
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get user by email"""
    from models import User
    return User.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    """Get user by ID"""
    from models import User
    return User.query.get(int(user_id))

def get_active_user_by_username(username):
    """Get active user by username"""
    from models import User
    return User.query.filter_by(username=username, is_active=True).first()

def validate_user_credentials(username, password):
    """Validate user credentials"""
    user = get_active_user_by_username(username)
    if user and hasattr(user, 'check_password') and user.check_password(password):
        return user
    return None