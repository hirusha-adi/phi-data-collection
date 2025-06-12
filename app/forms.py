from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuestionEntryForm(FlaskForm):
    area = SelectField('Area', coerce=int)
    location = SelectField('Location', coerce=int)
    cockroaches = SelectField(
        'Cockroaches',
        choices=[('True', 'Yes'), ('False', 'No')],
        validators=[DataRequired()],
        coerce=str
    )
    submit = SubmitField('Submit')
