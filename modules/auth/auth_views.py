"""
Authentication views and routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import app
from forms import LoginForm
from .auth_queries import validate_user_credentials

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        # Handle both form submission and direct POST
        username = form.username.data if form.username.data else request.form.get('username')
        password = form.password.data if form.password.data else request.form.get('password')
        
        if username and password:
            user = validate_user_credentials(username, password)
            if user:
                login_user(user)
                next_page = request.args.get('next')
                if not next_page:
                    next_page = url_for('dashboard')
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(next_page)
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))