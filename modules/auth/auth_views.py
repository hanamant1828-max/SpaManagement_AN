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
        
        username = form.username.data
        password = form.password.data
        
        print(f"Login attempt - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"User not found: {username}")
            flash('Invalid username or password', 'danger')
            return render_template('login.html', form=form)

        print(f"User found: {user.username}, Active: {user.is_active}")
        
        # Check if user is active
        if not user.is_active:
            flash('Account is disabled', 'danger')
            return render_template('login.html', form=form)

        # Check password using multiple methods
        password_valid = False
        
        # Method 1: Check if user has check_password method
        if hasattr(user, 'check_password') and callable(getattr(user, 'check_password')):
            try:
                password_valid = user.check_password(password)
                print(f"Password check via user method: {password_valid}")
            except Exception as e:
                print(f"Error in user.check_password: {e}")
        
        # Method 2: Check password_hash with werkzeug
        if not password_valid and user.password_hash:
            try:
                password_valid = check_password_hash(user.password_hash, password)
                print(f"Password check via werkzeug: {password_valid}")
            except Exception as e:
                print(f"Error in check_password_hash: {e}")
        
        # Method 3: Fallback for plain text (demo purposes only)
        if not password_valid and hasattr(user, 'password') and user.password:
            password_valid = (user.password == password)
            print(f"Password check via plain text: {password_valid}")

        if password_valid:
            try:
                login_user(user, remember=form.remember.data)
                print(f"Login successful for user: {username}")
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('dashboard'))
            except Exception as e:
                print(f"Error during login_user: {e}")
                flash('Login failed due to system error', 'danger')
        else:
            print(f"Password validation failed for user: {username}")
            flash('Invalid username or password', 'danger')

    else:
        # Form validation failed
        if form.errors:
            print(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))