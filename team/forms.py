from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import Length, DataRequired, Email, ValidationError
from flask import flash
from team.models import User, Profile
from team.dates import today


positions_choices = [('goalkeeper', 'Goalkeeper'),
                     ('defender', 'Defender'),
                     ('midfielder', 'Midfielder'),
                     ('forward', 'Forward')]

pitch_positions = ('goalkeeper', 'defender', 'midfielder', 'forward')

type_choices = [('training', 'Training'), ('match', 'Match')]

pitch_choices = [('training_ground', 'Training Ground'), ('stadium', 'Stadium')]


class LoginForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=2, max=40), DataRequired()])
    submit = SubmitField('Login')


class AddPlayerForm(FlaskForm):
    email_address = StringField('Email address', validators=[Length(min=2, max=40), DataRequired(), Email()])
    first_name = StringField('First name', validators=[Length(min=2, max=20), DataRequired()])
    last_name = StringField('Last name', validators=[Length(min=2, max=20), DataRequired()])
    birth_date = DateField('Birth date', default=today)
    position = SelectField('Position', choices=positions_choices, validators=[DataRequired()])
    number = IntegerField('Number', validators=[DataRequired()])
    submit_create = SubmitField('Create player!')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError("Email address already exists!")

    def validate_number(self, number_to_check):
        number = Profile.query.filter_by(number=number_to_check.data).first()
        if number:
            raise ValidationError("Some player already has this number!")


class CreateMeetingForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    hour = TimeField('Hour', validators=[DataRequired()])
    type = SelectField('Type', choices=type_choices, validators=[DataRequired()])
    locality = StringField('Locality', validators=[Length(min=2, max=20), DataRequired()])
    pitch = SelectField('Pitch', choices=pitch_choices, validators=[DataRequired()])
    submit_create = SubmitField('Create meeting!')


class UpdatePlayerForm(FlaskForm):
    first_name = StringField('First name', validators=[Length(min=2, max=20)])
    last_name = StringField('Last name', validators=[Length(min=2, max=20)])
    birth_date = DateField('Birth date', default=None)
    position = SelectField('Position', choices=positions_choices)
    number = IntegerField('Number')
    submit_update = SubmitField('Update player!')


class UpdateMeetingForm(FlaskForm):
    date = DateField('Date')
    hour = TimeField('Hour')
    type = SelectField('Type', choices=type_choices)
    locality = StringField('Locality', validators=[Length(min=2, max=20)])
    pitch = SelectField('Pitch', choices=pitch_choices)
    submit_update = SubmitField('Update meeting!')


class UpdateAttendanceForm(FlaskForm):
    submit_update = SubmitField("Present")


class DeleteForm(FlaskForm):
    submit_delete = SubmitField('Confirm')


class PresentForm(FlaskForm):
    submit_present = SubmitField("Present")


class AbsentForm(FlaskForm):
    submit_absent = SubmitField("Absent")


class UndoForm(FlaskForm):
    submit_undo = SubmitField("Undo")


def form_errors(form):
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'{err_msg[0]}', category='danger')

