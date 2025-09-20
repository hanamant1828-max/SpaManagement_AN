"""
Authentication views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, current_user
from sqlalchemy import func, or_, and_
from app import app, db
from forms import LoginForm
from .auth_queries import validate_user_credentials

@app.route('/test')
def test_route():
    """Simple test route to check connectivity"""
    return '''<!DOCTYPE html>
<html><head><title>Test Page</title></head>
<body style="font-family: Arial; padding: 50px; text-align: center;">
<h1 style="color: green;">✅ SUCCESS!</h1>
<h2>Spa Management System is Working</h2>
<p>If you can see this page, the server is working correctly.</p>
<p><a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Login Page</a></p>
</body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        from werkzeug.security import check_password_hash
        from models import User
        
        # Get user by identifier (username or email) - fallback for old form submissions
        identifier = form.identifier.data.strip().lower() if hasattr(form, 'identifier') else form.username.data.strip().lower()
        
        user = db.session.query(User).filter(
            or_(
                and_(User.email.isnot(None), func.lower(User.email) == identifier),
                func.lower(User.username) == identifier
            )
        ).first()
        print(f"Login attempt for identifier: {identifier}")
        print(f"User found: {user is not None}")
        
        # Check password validation
        password_valid = False
        if user:
            print(f"User is active: {user.is_active}")
            
            # Try multiple password validation methods
            if hasattr(user, 'check_password') and callable(user.check_password):
                try:
                    password_valid = user.check_password(form.password.data)
                    print(f"check_password method result: {password_valid}")
                except Exception as e:
                    print(f"Error with check_password method: {e}")
            
            # If user method fails or doesn't exist, try werkzeug directly
            if not password_valid and user.password_hash:
                try:
                    password_valid = check_password_hash(user.password_hash, form.password.data)
                    print(f"check_password_hash result: {password_valid}")
                except Exception as e:
                    print(f"Error with check_password_hash: {e}")
            
            # No plaintext password fallback for security

        if user and user.is_active and password_valid:
            login_user(user, remember=form.remember.data)
            print(f"Login successful for user: {user.username}")
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
        else:
            print(f"Login failed - User: {user is not None}, Active: {user.is_active if user else False}, Password Valid: {password_valid}")
            flash('Invalid username or password', 'danger')

    # If form validation fails, show errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')

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
            
        identifier = data.get('identifier', '').strip().lower()
        password = data.get('password', '')
        
        print(f"🔍 API Login attempt for identifier: '{identifier}'")
        
        if not identifier or not password:
            print("❌ API Login: Missing identifier or password")
            return jsonify({"success": False, "message": "Username/email and password are required"}), 400
        
        # Import models here to avoid circular imports
        from models import User
        
        # Lookup by email (case-insensitive) OR username (case-insensitive)
        # Handle cases where email might be None
        user = db.session.query(User).filter(
            or_(
                and_(User.email.isnot(None), func.lower(User.email) == identifier),
                func.lower(User.username) == identifier
            )
        ).first()
        
        print(f"🔍 User found: {user is not None}")
        if user:
            print(f"🔍 User details: username={user.username}, email={user.email}, active={user.is_active}")
        
        if not user:
            print(f"❌ API Login: No user found for identifier '{identifier}'")
            return jsonify({"success": False, "message": "Incorrect username/email or password."}), 401
            
        # Check if user is active
        if not user.is_active:
            print(f"❌ API Login: User {user.username} is inactive")
            return jsonify({"success": False, "message": "Your account is inactive. Please contact admin."}), 403
        
        # Verify password
        password_valid = False
        print(f"🔍 Testing password for user: {user.username}")
        
        if hasattr(user, 'check_password') and callable(user.check_password):
            try:
                password_valid = user.check_password(password)
                print(f"🔍 user.check_password() result: {password_valid}")
            except Exception as e:
                print(f"❌ Password check error: {e}")
        
        # If password validation fails, try werkzeug directly as fallback
        if not password_valid and user.password_hash:
            try:
                from werkzeug.security import check_password_hash
                password_valid = check_password_hash(user.password_hash, password)
                print(f"🔍 check_password_hash() result: {password_valid}")
            except Exception as e:
                print(f"❌ Password hash check error: {e}")
        
        if not password_valid:
            print(f"❌ API Login: Password validation failed for user {user.username}")
            return jsonify({"success": False, "message": "Incorrect username/email or password."}), 401
        
        # Login successful - create session (Flask handles cookie automatically)
        login_user(user, remember=True)
        
        # Create response - Flask will automatically handle session cookies
        resp = jsonify({"success": True, "message": "Login successful", "redirect": url_for('dashboard')})
        
        print(f"✅ API Login successful for user: {user.username}")
        return resp, 200
        
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