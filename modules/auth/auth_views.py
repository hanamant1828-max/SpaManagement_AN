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
    if form.validate_on_submit():
        user = validate_user_credentials(form.username.data, form.password.data)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('dashboard')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))