from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired, Email


class CreateUserForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    first_name = StringField('First name', validators=[Length(min=2, max=20), DataRequired()])
    last_name = StringField('Last name', validators=[Length(min=2, max=20), DataRequired()])
    position = SelectField('Position', choices=[('GK', 'Goalkeeper'),
                                                ('DF', 'Defender'),
                                                ('MF', 'Midfielder'),
                                                ('FR', 'Forward')],
                           validators=[DataRequired()])
    submit = SubmitField('Create player!')


class LoginForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=2, max=40), DataRequired])
