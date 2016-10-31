from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired,Length,EqualTo

class SignUpForm(FlaskForm):
    username = TextField('Username',[
    DataRequired(),
    Length(min=6, max=25)
    ])
    email = TextField('Email Address',[
    DataRequired(),
    Length(min=6,max=35)
    ])
    password = PasswordField('Enter Password',[
    DataRequired(),
    Length(min=6),
    EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the terms and conditions of service',[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = TextField('Username',[
        DataRequired(),
        Length(min=6, max=25)
    ])
    password = PasswordField('Enter Password',[
        DataRequired(),
        Length(min=6)
    ])
    login = SubmitField("Login")
