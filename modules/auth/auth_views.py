"""
Authentication views and routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import app
from forms import LoginForm
from .auth_queries import validate_user_credentials
# Assuming User model is available, e.g., from app.models import User
# If not, this import needs to be adjusted or the logic in the login route needs to be adapted.
# For the purpose of this change, we will assume 'User' is correctly imported or available.
from models import User # This is a placeholder, adjust as per your project structure

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
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))