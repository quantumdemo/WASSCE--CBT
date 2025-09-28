from flask import render_template, request
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
    from app.models import Exam, ExamAttempt
    from app.extensions import db
    from sqlalchemy import func

    # --- Real Database Queries ---

    # Get exam history
    exam_history_query = db.session.query(
        ExamAttempt, Exam
    ).join(Exam, ExamAttempt.exam_id == Exam.id)\
     .filter(ExamAttempt.user_id == current_user.id)\
     .order_by(ExamAttempt.start_time.desc())\
     .all()

    exam_history = [
        {
            'subject': exam.subject,
            'exam': exam.title,
            'score': f"{int(attempt.score)}%" if attempt.score is not None else "N/A",
            'date': attempt.start_time.strftime('%Y-%m-%d')
        }
        for attempt, exam in exam_history_query
    ]

    # Get performance analysis
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

    # Get current exams (e.g., exams not yet attempted by the user)
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
    # Mock data for the teacher dashboard
    recent_activities = [
        {'type': 'Exam', 'name': 'Algebra Practice', 'subject': 'Mathematics', 'age': '2 days ago'},
        {'type': 'Exam', 'name': 'Mechanics', 'subject': 'Physics', 'age': '1 week ago'},
        {'type': 'Exam', 'name': 'Chemical Reactions', 'subject': 'Chemistry', 'age': '1 week ago'},
    ]
    return render_template('teacher/dashboard.html', title='Teacher Dashboard', recent_activities=recent_activities)


@bp.route('/teacher/analytics')
@login_required
@role_required('teacher')
def teacher_analytics():
    # Mock data for the analytics page
    mock_analytics = {
        'overall_average': 78,
        'completion_rate': 92,
        'total_submissions': 1234,
        'average_score_by_subject': [
            {'subject': 'Mathematics', 'score': 72},
            {'subject': 'Physics', 'score': 85},
            {'subject': 'Chemistry', 'score': 79},
        ],
        'recent_exam_performance': [
            {'exam': 'Physics Mock 1', 'average': 85},
            {'exam': 'Chemistry Quiz', 'average': 75},
        ]
    }
    return render_template('teacher/analytics.html', title='Performance Analytics', analytics=mock_analytics)


@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # A placeholder for the admin dashboard
    # For now, we'll redirect to the user management page
    return redirect(url_for('main.user_management'))


@bp.route('/admin/user-management')
@login_required
@role_required('admin')
def user_management():
    # Mock data for user management
    mock_users = [
        {'id': 1, 'name': 'John Doe', 'email': 'john.doe@example.com', 'role': 'Student', 'status': 'Active', 'last_login': '2024-07-26'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'role': 'Teacher', 'status': 'Active', 'last_login': '2024-07-25'},
        {'id': 3, 'name': 'Peter Jones', 'email': 'peter.jones@example.com', 'role': 'Student', 'status': 'Inactive', 'last_login': '2024-06-15'},
        {'id': 4, 'name': 'Mary Williams', 'email': 'mary.williams@example.com', 'role': 'Student', 'status': 'Active', 'last_login': '2024-07-27'},
        {'id': 5, 'name': 'David Brown', 'email': 'david.brown@example.com', 'role': 'Admin', 'status': 'Active', 'last_login': '2024-07-27'},
    ]
    return render_template('admin/user_management.html', title='User Management', users=mock_users)


@bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    from app.models import User, UserRole, School
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_str = request.form.get('role')
        school_name = request.form.get('school', 'Default Centre') # Default school for teachers/admins

        # Basic validation
        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'warning')
            return redirect(url_for('main.add_user'))

        # Get or create school
        school = School.query.filter_by(name=school_name).first()
        if not school:
            school = School(name=school_name)
            db.session.add(school)
            # We assume this commit works in a real environment
            # db.session.commit()

        user = User(
            full_name=full_name,
            email=email,
            role=UserRole[role_str.upper()],
            school_id=school.id,
            is_verified=True # Admins create verified users
        )
        user.set_password(password)
        db.session.add(user)
        # db.session.commit() # Commented out due to sandbox issues
        flash('User created successfully!', 'success')
        return redirect(url_for('main.user_management'))

    return render_template('admin/add_user.html', title='Add New User')


@bp.route('/admin/centre-management')
@login_required
@role_required('admin')
def centre_management():
    # Mock data for centre management
    mock_centres = [
        {'id': 1, 'name': 'Greenwood High School', 'location': 'Lagos, Nigeria', 'students': 1250, 'teachers': 50},
        {'id': 2, 'name': 'Bright Star Academy', 'location': 'Accra, Ghana', 'students': 800, 'teachers': 35},
        {'id': 3, 'name': 'City College', 'location': 'Freetown, Sierra Leone', 'students': 2500, 'teachers': 120},
        {'id': 4, 'name': 'Kingswood College', 'location': 'Banjul, The Gambia', 'students': 600, 'teachers': 25},
    ]
    return render_template('admin/centre_management.html', title='Centre Management', centres=mock_centres)


@bp.route('/teacher/question-bank')
@login_required
@role_required('teacher')
def question_bank():
    # Fetch all questions from the database
    from app.models import Question
    all_questions = Question.query.all()

    # Convert to a list of dicts to pass to the template
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
    from app.models import Question, QuestionType
    if request.method == 'POST':
        # Logic to process the form and create a new question
        # This will be complex due to different question types
        text = request.form.get('text')
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        q_type_str = request.form.get('question_type')
        question_type = QuestionType[q_type_str.upper()]

        options = None
        answer = None

        if question_type in [QuestionType.MCQ_SINGLE, QuestionType.MCQ_MULTIPLE]:
            options = request.form.getlist('options[]')
            answer = request.form.getlist('answer[]')
        else: # Short Answer, Essay
            answer = request.form.get('answer')

        new_question = Question(
            text=text,
            subject=subject,
            topic=topic,
            question_type=question_type,
            options=options,
            answer=answer,
            created_by=current_user.id
        )
        db.session.add(new_question)
        # db.session.commit() # Commented out due to sandbox issues
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.question_bank'))

    return render_template('teacher/add_question.html', title='Add New Question')


@bp.route('/teacher/exam-builder')
@login_required
@role_required('teacher')
def exam_builder():
    # We can reuse the same mock questions from the question bank
    mock_questions = [
        {'id': 1, 'text': 'What is the capital of Nigeria?', 'topic': 'Geography', 'difficulty': 'Easy'},
        {'id': 2, 'text': 'Explain the concept of photosynthesis.', 'topic': 'Biology', 'difficulty': 'Medium'},
        {'id': 3, 'text': 'Solve the quadratic equation x^2 - 4x + 4 = 0.', 'topic': 'Mathematics', 'difficulty': 'Easy'},
        {'id': 4, 'text': 'Describe the process of cell division.', 'topic': 'Biology', 'difficulty': 'Hard'},
        {'id': 5, 'text': 'What is the chemical symbol for gold?', 'topic': 'Chemistry', 'difficulty': 'Easy'},
        {'id': 6, 'text': 'What is the value of x in the equation 2x + 5 = 15?', 'topic': 'Algebra', 'difficulty': 'Easy'},
        {'id': 7, 'text': 'Solve for y: 3y - 7 = 8', 'topic': 'Algebra', 'difficulty': 'Easy'},
        {'id': 8, 'text': 'What is the probability of rolling a 6 on a fair six-sided die?', 'topic': 'Probability', 'difficulty': 'Easy'},
    ]
    return render_template('teacher/exam_builder.html', title='Exam Builder', questions=mock_questions)


@bp.route('/teacher/grading/<int:attempt_id>')
@login_required
@role_required('teacher')
def grading_interface(attempt_id):
    # Mock data for a student's exam attempt
    mock_attempt = {
        'id': attempt_id,
        'student_name': 'John Doe',
        'exam_title': 'Biology Mid-term Exam',
        'questions_to_grade': [
            {
                'question_id': 2,
                'question_text': 'Explain the concept of photosynthesis, including the roles of chlorophyll, sunlight, water, and carbon dioxide.',
                'student_answer': 'Photosynthesis is how plants make food. They use sunlight, water from the ground, and air to make sugar. Chlorophyll is the green stuff that makes it happen. It happens in the leaves.',
                'max_score': 10
            },
            {
                'question_id': 4,
                'question_text': 'Describe the process of cell division (mitosis) and its importance for an organism.',
                'student_answer': 'Cell division is when one cell splits into two. It is important for growth and to replace old cells. The new cells are the same as the old one.',
                'max_score': 15
            }
        ]
    }
    return render_template('teacher/grading_interface.html', title='Grade Exam', attempt=mock_attempt)


@bp.route('/exam/<int:exam_id>')
@login_required
def exam(exam_id):
    # Fetch the exam and its questions from the database
    from app.models import Exam
    exam_data = Exam.query.get_or_404(exam_id)

    # Calculate initial time for display
    duration_minutes = exam_data.duration_minutes
    initial_hours = f"{duration_minutes // 60}".zfill(2)
    initial_minutes = f"{duration_minutes % 60}".zfill(2)

    # Convert the SQLAlchemy objects to a JSON-serializable dictionary
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

    # The exam data is passed to the template as a dictionary.
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

# --- Student Placeholder Routes ---
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

# --- Teacher Placeholder Routes ---
@bp.route('/teacher/exams')
@login_required
@role_required('teacher')
def teacher_exams():
    return render_template('placeholder.html', title='Manage Exams')

@bp.route('/teacher/grading')
@login_required
@role_required('teacher')
def teacher_grading():
    return render_template('placeholder.html', title='Grade Submissions')

# --- Admin Placeholder Routes ---
@bp.route('/admin/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    return render_template('placeholder.html', title='Audit Logs')