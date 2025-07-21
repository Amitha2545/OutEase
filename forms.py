from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,DateField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import TextAreaField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
class ApplyOutpassForm(FlaskForm):
    reason = TextAreaField("Reason for Outpass", validators=[DataRequired()])
    
    from_date = DateField("From Date", format='%Y-%m-%d', validators=[DataRequired()])
    to_date = DateField("To Date", format='%Y-%m-%d', validators=[DataRequired()])
    
    warden_required = BooleanField("Require Warden Approval?")
    
    
    submit = SubmitField("Apply")


from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    p_email = StringField("Parent mail", validators=[DataRequired(), Length(max=100)])
    gender = SelectField("Gender", choices=[('select','select'),('Male', 'Male'), ('Female', 'Female')])
    phone = StringField("Phone", validators=[Length(max=20)])
    address = StringField("Address", validators=[Length(max=200)])
    sidno=StringField("sidno", validators=[Length(max=20)])
    branch=SelectField("branch", choices=[('CSE','CSE'), ('ECE', 'ECE'),('EEE','EEE'),('CIVIL','CIVIL'),('MECH','MECH')])
    batch=SelectField("batch", choices=[('O20','O20'), ('O21', 'O21'),('O22','O22'),('O23','O23'),('O24','O24'),('O25','O25')])
    submit = SubmitField("Save Changes")
