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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = validate_user_credentials(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('dashboard')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    elif request.method == 'POST':
        # Handle form validation errors
        flash('Please check your input and try again', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))