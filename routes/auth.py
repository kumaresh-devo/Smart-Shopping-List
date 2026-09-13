import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome, {user.name}', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.dashboard_view'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'warning')
            return render_template('auth/signup.html', name=name, email=email)

        if not re.match(EMAIL_REGEX, email):
            flash('Please provide a valid email address.', 'warning')
            return render_template('auth/signup.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/signup.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html', name=name, email=email)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'info')
            return redirect(url_for('auth.login'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))

    reset_url = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your registered email address.', 'warning')
            return render_template('auth/forgot_password.html')

        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash('Password reset link generated successfully! You can use the link below to reset your password.', 'success')
        else:
            flash('If that email is registered, a password reset link has been created.', 'info')

    return render_template('auth/forgot_password.html', reset_url=reset_url)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))

    user = User.verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Please fill in both password fields.', 'warning')
            return render_template('auth/reset_password.html', token=token)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(password)
        db.session.commit()

        flash('Your password has been reset successfully! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
