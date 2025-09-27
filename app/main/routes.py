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

    # Mock data for demonstration purposes
    current_exams = [
        {'subject': 'Mathematics', 'title': 'Mock Exam 1', 'starts_in': '2 days'}
    ]

    performance_analysis = [
        {'subject': 'Mathematics', 'score': 65},
        {'subject': 'Physics', 'score': 75},
        {'subject': 'Chemistry', 'score': 82},
        {'subject': 'Biology', 'score': 68},
    ]
    overall_performance = int(sum(p['score'] for p in performance_analysis) / len(performance_analysis))


    exam_history = [
        {'subject': 'Physics', 'exam': 'Mock Exam 1', 'score': '75%', 'date': '2024-07-20'},
        {'subject': 'Chemistry', 'exam': 'Mock Exam 1', 'score': '82%', 'date': '2024-07-15'},
        {'subject': 'Biology', 'exam': 'Mock Exam 1', 'score': '68%', 'date': '2024-07-10'},
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
    # Mock data for the question bank
    mock_questions = [
        {
            'id': 1,
            'text': 'What is the capital of Nigeria?',
            'subject': 'Geography',
            'topic': 'General Knowledge',
            'type': 'MCQ'
        },
        {
            'id': 2,
            'text': 'Explain the concept of photosynthesis.',
            'subject': 'Biology',
            'topic': 'Botany',
            'type': 'Essay'
        },
        {
            'id': 3,
            'text': 'Solve the quadratic equation x^2 - 4x + 4 = 0.',
            'subject': 'Mathematics',
            'topic': 'Algebra',
            'type': 'Short Answer'
        },
        {
            'id': 4,
            'text': 'Describe the process of cell division.',
            'subject': 'Biology',
            'topic': 'Cell Biology',
            'type': 'Essay'
        },
        {
            'id': 5,
            'text': 'What is the chemical symbol for gold?',
            'subject': 'Chemistry',
            'topic': 'Inorganic Chemistry',
            'type': 'MCQ'
        }
    ]
    return render_template('teacher/question_bank.html', title='Question Bank', questions=mock_questions)


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
    # Mock data for a single exam
    # In a real app, this would be fetched from the database based on exam_id
    mock_exam = {
        'id': exam_id,
        'title': 'WASSCE Practice Exam',
        'duration_minutes': 60,
        'questions': [
            {
                'id': 1,
                'text': 'Which of the following is NOT a characteristic of a good research question?',
                'type': 'mcq_single',
                'options': [
                    'It is clear and concise',
                    'It is broad and open-ended',
                    'It is focused and specific',
                    'It is relevant to the field of study'
                ]
            },
            {
                'id': 2,
                'text': 'Solve for x in the equation 2x + 5 = 15.',
                'type': 'short_answer',
                'options': []
            },
            {
                'id': 3,
                'text': 'Which of these are primary colors?',
                'type': 'mcq_multiple',
                'options': [
                    'Red',
                    'Green',
                    'Blue',
                    'Yellow'
                ]
            },
            {
                'id': 4,
                'text': 'What is the capital of Ghana?',
                'type': 'short_answer',
                'options': []
            }
            # Add more questions as needed to test navigation
        ]
    }
    return render_template('exam_interface.html', title=mock_exam['title'], exam=mock_exam)