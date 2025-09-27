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
    # A placeholder for the teacher dashboard
    return "<h1>Teacher Dashboard</h1>"

@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # A placeholder for the admin dashboard
    return "<h1>Admin Dashboard</h1>"


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