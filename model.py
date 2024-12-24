from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin
from sqlalchemy import LargeBinary
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    sub_taught = db.Column(db.String)
    sub_studies = db.Column(db.String)

    @property
    def is_active(self):
        return True  

    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Subjects(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sname = db.Column(db.String, unique=False)
    prof_list = db.Column(db.String, nullable=False)
    stud_list = db.Column(db.String, nullable=False)

class Lecture(db.Model):
    __tablename__ = 'lecture'
    lec_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lec_name = db.Column(db.String)
    insti_note = db.Column(LargeBinary, nullable=False)
    url = db.Column(db.String, nullable=False)
    trans = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    flashcard = db.Column(db.Text)

class Student_notes(db.Model):
    __tablename__ = 'student_notes'
    snote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    s_note = db.Column(LargeBinary, nullable=True)
    s_url = db.Column(db.String, nullable=True)
    s_id = db.Column(db.Integer) 
    notes = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    flashcard = db.Column(db.Text)

class Scores(db.Model):
    __tablename__ = 'scores'
    quiz_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    timestmp = db.Column(db.String)
    lec_id = db.Column(db.Integer)
    stu_id = db.Column(db.Integer)
    score = db.Column(db.Integer)

class JoinRequest(db.Model):
    __tablename__ = 'join_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer)
    role = db.Column(db.String)  # 'student' or 'professor'
    status = db.Column(db.String)  # 'pending', 'approved', 'rejected'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)