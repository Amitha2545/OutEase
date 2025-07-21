from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')
    idno = db.Column(db.String(20))  # University/college ID number
    branch = db.Column(db.String(50))             # E.g., CSE, ECE
    batch = db.Column(db.String(20)) 
    p_email = db.Column(db.String(120))
    # Relationship: One student can have many outpasses
    outpasses = db.relationship('Outpass', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Outpass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    reason = db.Column(db.Text, nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # Auto submission time
    
    status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected
    warden_required = db.Column(db.Boolean, default=False)
    
    security_exit =db.Column(db.String(20), default='Pending')
    # Approval Status Fields
    exited_at=db.Column(db.DateTime,default=datetime.utcnow)
    warden_approval = db.Column(db.String(20), default="Not Requested")
    warden_status = db.Column(db.String(20), default=None)
    
