from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager
import enum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserRole(enum.Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship('User', backref='school', lazy=True)

    def __repr__(self):
        return f'<School {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True) # Nullable for super admins

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class QuestionType(enum.Enum):
    MCQ_SINGLE = 'mcq_single'
    MCQ_MULTIPLE = 'mcq_multiple'
    SHORT_ANSWER = 'short_answer'
    ESSAY = 'essay'
    COMPREHENSION = 'comprehension'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False) # Can store HTML for rich formatting
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    options = db.Column(db.JSON, nullable=True) # For MCQ options
    answer = db.Column(db.JSON, nullable=False) # Can be a single value or a list
    explanation = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Teacher ID
    version = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f'<Question {self.id}>'

# Association table for the many-to-many relationship between Exam and Question
exam_questions = db.Table('exam_questions',
    db.Column('exam_id', db.Integer, db.ForeignKey('exam.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Teacher ID
    questions = db.relationship('Question', secondary=exam_questions, lazy='subquery',
                                backref=db.backref('exams', lazy=True))

    def __repr__(self):
        return f'<Exam {self.title}>'

class ExamAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    answers = db.Column(db.JSON, nullable=True) # Stores student's answers: {question_id: answer}

    user = db.relationship('User', backref='attempts')
    exam = db.relationship('Exam', backref='attempts')

    def __repr__(self):
        return f'<ExamAttempt {self.id} by User {self.user_id}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Grader
    score = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text, nullable=True)

    attempt = db.relationship('ExamAttempt', backref='grades')
    question = db.relationship('Question')
    teacher = db.relationship('User')

    def __repr__(self):
        return f'<Grade for Attempt {self.attempt_id} on Question {self.question_id}>'