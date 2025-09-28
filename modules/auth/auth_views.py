"""
Authentication views and routes
"""
import os
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import func, or_, and_
from app import app, db
from forms import LoginForm
from .auth_queries import validate_user_credentials
from datetime import datetime

# Password verification function with fallback (hash drift)
def verify_pwd(stored, given):
    """Robust password verification supporting current and legacy hashes"""
    if not stored or not given:
        return False
        
    # bcrypt hashes
    if stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$"):
        try:
            import bcrypt
            return bcrypt.checkpw(given.encode(), stored.encode())
        except Exception:
            return False
    
    # werkzeug pbkdf2 hashes (default)
    try:
        from werkzeug.security import check_password_hash
        return check_password_hash(stored, given)
    except Exception:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        from werkzeug.security import check_password_hash
        from models import User
        
        # Get form data directly for better debugging
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"Login attempt for username: {username}")
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        # Find user by username (case-insensitive)
        user = User.query.filter(func.lower(User.username) == username.lower()).first()
        print(f"User found: {user is not None}")
        
        if user:
            print(f"User is active: {user.is_active}")
            print(f"User has password_hash: {user.password_hash is not None}")
            
            # Check password
            password_valid = False
            if user.password_hash:
                try:
                    password_valid = check_password_hash(user.password_hash, password)
                    print(f"Password validation result: {password_valid}")
                except Exception as e:
                    print(f"Error checking password: {e}")
                    
                # If standard check fails, try user's check_password method
                if not password_valid and hasattr(user, 'check_password'):
                    try:
                        password_valid = user.check_password(password)
                        print(f"User method password check: {password_valid}")
                    except Exception as e:
                        print(f"Error with user check_password: {e}")
            
            if password_valid and user.is_active:
                login_user(user, remember=request.form.get('remember') == 'on')
                print(f"Login successful for user: {user.username}")
                flash('Login successful!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                print(f"Login failed - Password valid: {password_valid}, Active: {user.is_active}")
                flash('Invalid username or password', 'danger')
        else:
            print("User not found")
            flash('Invalid username or password', 'danger')
    
    # For GET requests or failed POST, show login form
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint that supports both username and email"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            print("❌ API Login: No JSON data received")
            return jsonify({"success": False, "message": "Invalid request format"}), 400
        
        # Normalize + lookup by username OR email (case-insensitive)    
        identifier = data.get("identifier", "").strip()
        password = data.get("password", "")
        ident_l = identifier.lower()
        
        print(f"🔍 API Login attempt for identifier: '{identifier}' (normalized: '{ident_l}')")
        
        if not identifier or not password:
            print("❌ API Login: Missing identifier or password")
            return jsonify({"success": False, "message": "Username/email and password are required"}), 400
        
        # Import models here to avoid circular imports
        from models import User
        from sqlalchemy import or_, func
        
        # Normalize + lookup by username OR email (case-insensitive)
        user = (db.session.query(User)
                .filter(or_(func.lower(User.username) == ident_l,
                           func.lower(User.email) == ident_l))
                .first())
        
        print(f"🔍 User found: {user is not None}")
        if user:
            print(f"🔍 User details: username={user.username}, email={user.email}, active={user.is_active}")
        
        if not user:
            print(f"❌ API Login: No user found for identifier '{identifier}'")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
        # User status checks (don't silently fail)
        if hasattr(user, 'is_active') and not user.is_active:
            print(f"❌ API Login: User {user.username} is inactive")
            return jsonify({"success": False, "message": "Your account is inactive."}), 403
        
        # Password verification with fallback (hash drift)
        print(f"🔍 Testing password for user: {user.username}")
        
        if not verify_pwd(user.password_hash, password):
            print(f"❌ API Login: Invalid password for user {user.username}")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
        # Login successful - clear and set session 
        print(f"✅ API Login successful for user: {user.username}")
        session.clear()
        session["uid"] = user.id
        login_user(user)
        
        # Update last login time if column exists
        try:
            if hasattr(user, 'last_login'):
                user.last_login = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            print(f"Warning: Could not update last_login: {e}")
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        print(f"❌ API login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "An error occurred during login"}), 500

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route - Admin only in production"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Disable public registration in production - admin only
    import os
    if os.environ.get('FLASK_ENV') != 'development':
        flash('Registration is disabled. Please contact an administrator.', 'warning')
        return redirect(url_for('login'))
    
    from forms import UserRegistrationForm
    form = UserRegistrationForm()
    
    if form.validate_on_submit():
        try:
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Create new user
            user = User(
                username=form.username.data.lower().strip(),
                email=form.email.data.lower().strip(),
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                phone=form.phone.data.strip() if form.phone.data else None,
                password_hash=generate_password_hash(form.password.data),
                role='staff',  # Default role for new registrations
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    """User profile management route"""
    from forms import UserProfileForm
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            # Update user profile
            current_user.first_name = form.first_name.data.strip()
            current_user.last_name = form.last_name.data.strip()
            current_user.email = form.email.data.lower().strip()
            current_user.phone = form.phone.data.strip() if form.phone.data else None
            current_user.date_of_birth = form.date_of_birth.data
            current_user.gender = form.gender.data if form.gender.data else None
            current_user.notes_bio = form.notes_bio.data.strip() if form.notes_bio.data else None
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Profile update failed. Please try again.', 'danger')
            print(f"Profile update error: {e}")
    
    return render_template('user_profile.html', form=form, user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route"""
    from forms import ChangePasswordForm
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            from werkzeug.security import generate_password_hash
            
            # Update password
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('user_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Password change failed. Please try again.', 'danger')
            print(f"Password change error: {e}")
    
    return render_template('change_password.html', form=form)

# Dev-only admin reset route (guarded)
@app.route("/dev/reset-admin", methods=['POST'])
def dev_reset_admin():
    """Development-only route to create or reset admin user"""
    # Only allow in development environment
    if os.getenv("FLASK_ENV") != "development":
        return jsonify({"success": False, "message": "forbidden"}), 403
        
    try:
        from models import User
        from sqlalchemy import func
        from werkzeug.security import generate_password_hash
        
        username = "admin"
        email = "admin@example.com"
        plain = "admin123"
        
        # Find existing admin user (case-insensitive)
        u = User.query.filter(func.lower(User.username) == "admin").first()
        if not u:
            # Create new admin user
            u = User(
                username=username, 
                email=email, 
                first_name="Admin",
                last_name="User",
                is_active=True, 
                role="admin"
            )
            db.session.add(u)
            print(f"🔧 Creating new admin user: {username}")
        else:
            # Update existing admin user
            u.email = email
            u.is_active = True
            u.role = "admin"
            print(f"🔧 Updating existing admin user: {username}")
        
        # Set pbkdf2 hash (werkzeug default)
        u.password_hash = generate_password_hash(plain)  # pbkdf2:sha256
        db.session.commit()
        
        print(f"✅ Admin user reset successful: {username}/{plain}")
        return jsonify({"success": True, "message": "Admin reset to admin/admin123"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Admin reset error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Error resetting admin: {str(e)}"}), 500