
from app import app, db
from models import User

with app.app_context():
    user = User.query.get(1)
    if user:
        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print(f"Has can_access method: {hasattr(user, 'can_access')}")
        if hasattr(user, 'can_access'):
            print(f"Can access packages: {user.can_access('packages')}")
        print(f"User attributes: {dir(user)}")
    else:
        print("User with ID 1 not found")
