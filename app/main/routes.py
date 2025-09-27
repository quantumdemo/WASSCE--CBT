from flask import render_template
from flask_login import login_required, current_user
from app.main import bp
from app.decorators import role_required

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    # This will be the student dashboard
    return render_template('student_dashboard.html', title='Dashboard')

@bp.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    # A placeholder for the teacher dashboard
    return "<h1>Teacher Dashboard</h1>"

@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # A placeholder for the admin dashboard
    return "<h1>Admin Dashboard</h1>"