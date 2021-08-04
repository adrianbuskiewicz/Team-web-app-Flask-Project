from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, FileField, SubmitField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import Length, DataRequired, Email
from flask import flash


positions_choices = [('goalkeeper', 'Goalkeeper'),
                     ('defender', 'Defender'),
                     ('midfielder', 'Midfielder'),
                     ('forward', 'Forward')]

type_choices = [('training', 'Training'),('match', 'Match')]

pitch_choices = [('training_ground', 'Training Ground'), ('stadium', 'Stadium')]


class AddPlayerForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    first_name = StringField('First name', validators=[Length(min=2, max=20), DataRequired()])
    last_name = StringField('Last name', validators=[Length(min=2, max=20), DataRequired()])
    birth_date = DateField('Birth date', default=None)
    position = SelectField('Position', choices=positions_choices, validators=[DataRequired()])
    number = IntegerField('Number', validators=[DataRequired()])
    submit = SubmitField('Create player!')


class CreateMeetingForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    hour = TimeField('Hour', validators=[DataRequired()])
    type = SelectField('Type', choices=type_choices, validators=[DataRequired()])
    locality = StringField('Locality', validators=[Length(min=2, max=20), DataRequired()])
    pitch = SelectField('Pitch', choices=pitch_choices, validators=[DataRequired()])
    submit = SubmitField('Create meeting!')


class LoginForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=2, max=40), DataRequired()])
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    birth_date = DateField('Birth date', validators=[DataRequired()], default=None)
    submit = SubmitField('Confirm changes')


def form_errors(form):
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'{err_msg[0]}', category='danger')