from app import create_app
from app.extensions import db
from app.models import User, School, Question, Exam, ExamAttempt, Grade

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'School': School,
        'Question': Question,
        'Exam': Exam,
        'ExamAttempt': ExamAttempt,
        'Grade': Grade
    }

if __name__ == '__main__':
    app.run(debug=True)