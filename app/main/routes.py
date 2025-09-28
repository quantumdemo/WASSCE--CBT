from flask import render_template, request, abort
from flask_login import login_required, current_user
from app.main import bp
from app.decorators import role_required
from app.models import Exam, ExamAttempt, User, School, Question, QuestionType, UserRole
from app.extensions import db
from sqlalchemy import func
from datetime import datetime

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    # --- Real Database Queries ---
    exam_history_query = db.session.query(
        ExamAttempt, Exam
    ).join(Exam, ExamAttempt.exam_id == Exam.id)\
     .filter(ExamAttempt.user_id == current_user.id)\
     .order_by(ExamAttempt.start_time.desc())\
     .all()

    exam_history = [
        {
            'subject': attempt.exam.subject,
            'exam': attempt.exam.title,
            'score': f"{int(attempt.score)}%" if attempt.score is not None else "N/A",
            'date': attempt.start_time.strftime('%Y-%m-%d')
        }
        for attempt, exam in exam_history_query
    ]

    performance_analysis_query = db.session.query(
        Exam.subject,
        func.avg(ExamAttempt.score)
    ).join(Exam, ExamAttempt.exam_id == Exam.id)\
     .filter(ExamAttempt.user_id == current_user.id, ExamAttempt.score.isnot(None))\
     .group_by(Exam.subject)\
     .all()

    performance_analysis = [
        {'subject': subject, 'score': int(avg_score)}
        for subject, avg_score in performance_analysis_query
    ]

    overall_performance = 0
    if performance_analysis:
        overall_performance = int(sum(p['score'] for p in performance_analysis) / len(performance_analysis))

    attempted_exam_ids = [attempt.exam_id for attempt, exam in exam_history_query]
    current_exams_query = Exam.query.filter(
        ~Exam.id.in_(attempted_exam_ids)
    ).limit(5).all()

    current_exams = [
        {'subject': exam.subject, 'title': exam.title, 'starts_in': 'Available Now'}
        for exam in current_exams_query
    ]

    return render_template('student_dashboard.html',
                           title='Dashboard',
                           current_exams=current_exams,
                           performance=performance_analysis,
                           overall_performance=overall_performance,
                           exam_history=exam_history)

@bp.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    recent_exams = Exam.query.filter_by(created_by=current_user.id)\
                             .order_by(Exam.creation_date.desc())\
                             .limit(5).all()

    now = datetime.utcnow()
    recent_activities = []
    for exam in recent_exams:
        age_seconds = (now - exam.creation_date).total_seconds()
        if age_seconds < 3600:
            age = f"{int(age_seconds / 60)} minutes ago"
        elif age_seconds < 86400:
            age = f"{int(age_seconds / 3600)} hours ago"
        else:
            age = f"{int(age_seconds / 86400)} days ago"

        recent_activities.append({
            'type': 'Exam',
            'name': exam.title,
            'subject': exam.subject,
            'age': age
        })

    return render_template('teacher/dashboard.html', title='Teacher Dashboard', recent_activities=recent_activities)

@bp.route('/teacher/analytics')
@login_required
@role_required('teacher')
def teacher_analytics():
    teacher_exams = Exam.query.filter_by(created_by=current_user.id).all()
    teacher_exam_ids = [e.id for e in teacher_exams]
    all_attempts = ExamAttempt.query.filter(ExamAttempt.exam_id.in_(teacher_exam_ids)).all()
    total_submissions = len(all_attempts)

    completed_attempts = [a for a in all_attempts if a.end_time is not None]
    completion_rate = int((len(completed_attempts) / total_submissions) * 100) if total_submissions > 0 else 0

    scored_attempts = [a.score for a in all_attempts if a.score is not None]
    overall_average = int(sum(scored_attempts) / len(scored_attempts)) if scored_attempts else 0

    average_score_by_subject_query = db.session.query(
        Exam.subject,
        func.avg(ExamAttempt.score)
    ).join(ExamAttempt, Exam.id == ExamAttempt.exam_id)\
     .filter(Exam.created_by == current_user.id, ExamAttempt.score.isnot(None))\
     .group_by(Exam.subject).all()

    average_score_by_subject = [
        {'subject': subject, 'score': int(avg_score)}
        for subject, avg_score in average_score_by_subject_query
    ]

    recent_exam_performance_query = db.session.query(
        Exam.title,
        func.avg(ExamAttempt.score)
    ).join(ExamAttempt, Exam.id == ExamAttempt.exam_id)\
     .filter(Exam.created_by == current_user.id)\
     .group_by(Exam.id)\
     .order_by(Exam.creation_date.desc())\
     .limit(5).all()

    recent_exam_performance = [
        {'exam': title, 'average': int(avg_score) if avg_score is not None else 0}
        for title, avg_score in recent_exam_performance_query
    ]

    analytics_data = {
        'total_submissions': total_submissions,
        'overall_average': overall_average,
        'completion_rate': completion_rate,
        'average_score_by_subject': average_score_by_subject,
        'recent_exam_performance': recent_exam_performance,
    }
    return render_template('teacher/analytics.html', title='Performance Analytics', analytics=analytics_data)

@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    return redirect(url_for('main.user_management'))

@bp.route('/admin/user-management')
@login_required
@role_required('admin')
def user_management():
    all_users = User.query.all()
    users_data = [
        {
            'id': user.id,
            'name': user.full_name,
            'email': user.email,
            'role': user.role.value.title(),
            'status': 'Active' if user.is_verified else 'Inactive',
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
        }
        for user in all_users
    ]
    return render_template('admin/user_management.html', title='User Management', users=users_data)

@bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_str = request.form.get('role')
        school_name = request.form.get('school', 'Default Centre')

        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'warning')
            return redirect(url_for('main.add_user'))

        school = School.query.filter_by(name=school_name).first()
        if not school:
            school = School(name=school_name)
            db.session.add(school)

        user = User(
            full_name=full_name,
            email=email,
            role=UserRole[role_str.upper()],
            school_id=school.id,
            is_verified=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('main.user_management'))

    return render_template('admin/add_user.html', title='Add New User')

@bp.route('/admin/centre-management')
@login_required
@role_required('admin')
def centre_management():
    all_schools = School.query.all()
    centres_data = []
    for school in all_schools:
        students_count = User.query.filter_by(school_id=school.id, role=UserRole.STUDENT).count()
        teachers_count = User.query.filter_by(school_id=school.id, role=UserRole.TEACHER).count()
        centres_data.append({
            'id': school.id,
            'name': school.name,
            'location': school.location or 'N/A',
            'students': students_count,
            'teachers': teachers_count
        })

    return render_template('admin/centre_management.html', title='Centre Management', centres=centres_data)

@bp.route('/teacher/question-bank')
@login_required
@role_required('teacher')
def question_bank():
    all_questions = Question.query.all()
    questions_data = [
        {
            'id': q.id,
            'text': q.text,
            'subject': q.subject,
            'topic': q.topic,
            'type': q.question_type.value
        } for q in all_questions
    ]
    return render_template('teacher/question_bank.html', title='Question Bank', questions=questions_data)

@bp.route('/teacher/question/new', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def add_question():
    if request.method == 'POST':
        new_question = Question(
            text=request.form.get('text'),
            subject=request.form.get('subject'),
            topic=request.form.get('topic'),
            question_type=QuestionType[request.form.get('question_type').upper()],
            options=request.form.getlist('options[]'),
            answer=request.form.getlist('answer[]') or request.form.get('answer'),
            created_by=current_user.id
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.question_bank'))

    return render_template('teacher/add_question.html', title='Add New Question')

@bp.route('/teacher/exam-builder')
@login_required
@role_required('teacher')
def exam_builder():
    all_questions = Question.query.all()
    questions_data = [
        {
            'id': q.id,
            'text': q.text,
            'topic': q.topic,
            'difficulty': q.difficulty
        }
        for q in all_questions
    ]
    return render_template('teacher/exam_builder.html', title='Exam Builder', questions=questions_data)

@bp.route('/teacher/grading')
@login_required
@role_required('teacher')
def grading_list():
    # Find attempts for exams created by the current teacher that need grading
    attempts_to_grade = ExamAttempt.query.join(Exam).filter(
        Exam.created_by == current_user.id,
        ExamAttempt.score.is_(None),
        ExamAttempt.end_time.isnot(None)
    ).order_by(ExamAttempt.end_time.desc()).all()

    attempts_data = [
        {
            'id': attempt.id,
            'student_name': attempt.user.full_name,
            'exam_title': attempt.exam.title,
            'submitted_on': attempt.end_time
        }
        for attempt in attempts_to_grade
    ]
    return render_template('teacher/grading_list.html', title='Exams to Grade', attempts=attempts_data)


@bp.route('/teacher/grading/<int:attempt_id>')
@login_required
@role_required('teacher')
def grading_interface(attempt_id):
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.exam.created_by != current_user.id:
        abort(403)

    questions_to_grade = []
    student_answers = attempt.answers or {}
    for question in attempt.exam.questions:
        if question.question_type in [QuestionType.ESSAY, QuestionType.SHORT_ANSWER]:
            questions_to_grade.append({
                'question_id': question.id,
                'question_text': question.text,
                'student_answer': student_answers.get(str(question.id), 'No answer provided.'),
                'max_score': question.max_score
            })

    attempt_data = {
        'id': attempt.id,
        'student_name': attempt.user.full_name,
        'exam_title': attempt.exam.title,
        'questions_to_grade': questions_to_grade
    }
    return render_template('teacher/grading_interface.html', title='Grade Exam', attempt=attempt_data)

@bp.route('/exam/<int:exam_id>')
@login_required
def exam(exam_id):
    exam_data = Exam.query.get_or_404(exam_id)
    duration_minutes = exam_data.duration_minutes
    initial_hours = f"{duration_minutes // 60}".zfill(2)
    initial_minutes = f"{duration_minutes % 60}".zfill(2)
    exam_dict = {
        'id': exam_data.id,
        'title': exam_data.title,
        'duration_minutes': duration_minutes,
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'type': q.question_type.value,
                'options': q.options
            } for q in exam_data.questions
        ]
    }
    return render_template('exam_interface.html',
                           title=exam_dict['title'],
                           exam=exam_dict,
                           initial_hours=initial_hours,
                           initial_minutes=initial_minutes)

# --- Placeholder Routes ---
@bp.route('/results')
@login_required
def results():
    return render_template('placeholder.html', title='Results')

@bp.route('/settings')
@login_required
def settings():
    return render_template('placeholder.html', title='Settings')

@bp.route('/student/practice')
@login_required
def student_practice():
    return render_template('placeholder.html', title='Practice View')

@bp.route('/student/mock-exams')
@login_required
def student_mock_exams():
    return render_template('placeholder.html', title='Mock Exams')

@bp.route('/student/past-questions')
@login_required
def student_past_questions():
    return render_template('placeholder.html', title='Past Questions')

@bp.route('/student/resources')
@login_required
def student_resources():
    return render_template('placeholder.html', title='Resources')

@bp.route('/teacher/exams')
@login_required
@role_required('teacher')
def teacher_exams():
    return render_template('placeholder.html', title='Manage Exams')

@bp.route('/admin/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    return render_template('placeholder.html', title='Audit Logs')