from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.auth import bp
from app.models import User, School
from app.email import send_email
import random
from datetime import datetime, timedelta

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # A main blueprint will be created later

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        school_name = request.form.get('school')

        # Basic validation
        if not all([full_name, email, password, school_name]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'warning')
            return redirect(url_for('auth.register'))

        # Get or create school
        school = School.query.filter_by(name=school_name).first()
        if not school:
            school = School(name=school_name)
            db.session.add(school)
            # We commit here to get the school ID
            db.session.commit()

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        otp_expiration = datetime.utcnow() + timedelta(minutes=10)

        user = User(
            full_name=full_name,
            email=email,
            school_id=school.id,
            otp=otp,
            otp_expiration=otp_expiration
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send verification email
        email_html = render_template('email/verify_otp.html', otp=otp)
        send_email(user.email, 'Verify Your EduPrep Account', email_html)

        flash('Registration successful! Please check your email for a verification code.', 'success')
        return redirect(url_for('auth.verify_otp', email=user.email))

    return render_template('auth/register.html', title='Register')


@bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    if not email:
        flash('An error occurred. Please try registering again.', 'danger')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        submitted_otp = request.form.get('otp')
        if user.otp == submitted_otp and user.otp_expiration > datetime.utcnow():
            User.query.filter_by(id=user.id).update({
                'is_verified': True,
                'otp': None,
                'otp_expiration': None
            })
            db.session.commit()
            flash('Your account has been successfully verified! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')

    return render_template('auth/verify_otp.html', title='Verify Account', email=email)


@bp.route('/resend-otp')
def resend_otp():
    email = request.args.get('email')
    if not email:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first_or_404()

    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expiration = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    # Send new verification email
    email_html = render_template('email/verify_otp.html', otp=otp)
    send_email(user.email, 'Your New EduPrep Verification Code', email_html)

    flash('A new verification code has been sent to your email.', 'success')
    return redirect(url_for('auth.verify_otp', email=user.email))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            # Re-render the form with an error instead of redirecting, to break the loop
            return render_template('auth/login.html', title='Login')

        # Check if the user is verified
        if not user.is_verified:
            flash('Your account is not verified. Please check your email for the verification code.', 'warning')
            return redirect(url_for('auth.verify_otp', email=user.email))

        login_user(user, remember=True)
        # Redirect to the appropriate dashboard based on role
        # This will be implemented more robustly later
        if user.role.value == 'teacher':
             return redirect(url_for('main.teacher_dashboard'))
        elif user.role.value == 'admin':
             return redirect(url_for('main.admin_dashboard'))
        else:
             return redirect(url_for('main.dashboard'))


    return render_template('auth/login.html', title='Login')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index')) # Redirect to landing page


@bp.route('/request-reset-token', methods=['GET', 'POST'])
def request_reset_token():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            email_html = render_template('email/reset_password.html', user=user, token=token)
            send_email(user.email, 'Password Reset Request', email_html)
            # For testing, we can flash the token or a link
            flash(f'TESTING: Password reset link: {url_for("auth.reset_token", token=token, _external=True)}', 'info')
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/request_reset_token.html', title='Reset Password')


@bp.route('/reset-token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('auth.request_reset_token'))
    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        # We will assume this commit works in a real environment
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password')