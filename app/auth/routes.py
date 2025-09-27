from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.auth import bp
from app.models import User, School

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

        user = User(full_name=full_name, email=email, school_id=school.id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register')

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