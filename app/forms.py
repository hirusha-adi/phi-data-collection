from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuestionEntryForm(FlaskForm):
    area = SelectField('Area', coerce=int, validators=[DataRequired()])
    location = SelectField('Location', coerce=int, validators=[DataRequired()])
    cockroaches = SelectField('Cockroaches', coerce=bool, choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    submit = SubmitField('Save')
