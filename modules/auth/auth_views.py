"""
Authentication views and routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import app
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
        
        # Get user by username
        user = User.query.filter_by(username=form.username.data).first()
        print(f"Login attempt for username: {form.username.data}")
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
            
            # Fallback for plain text password (development only)
            if not password_valid and hasattr(user, 'password') and user.password:
                password_valid = user.password == form.password.data
                print(f"Plain text password check: {password_valid}")

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

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))