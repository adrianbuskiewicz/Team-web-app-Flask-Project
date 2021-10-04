from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, PasswordField, SubmitField, IntegerField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import Length, DataRequired, Email, ValidationError, EqualTo
from flask import flash
from team.models import User, Profile

positions_choices = [
    ("goalkeeper", "Goalkeeper"),
    ("defender", "Defender"),
    ("midfielder", "Midfielder"),
    ("forward", "Forward"),
]

pitch_positions = ("goalkeeper", "defender", "midfielder", "forward")

type_choices = [("training", "Training"), ("match", "Match")]

pitch_choices = [("training_ground", "Training Ground"), ("stadium", "Stadium")]


class LoginForm(FlaskForm):
    email_address = StringField(
        "Email address", validators=[Length(min=2, max=40), DataRequired(), Email()]
    )
    password = PasswordField(
        "Password", validators=[Length(min=2, max=40), DataRequired()]
    )
    submit = SubmitField("Login")


class PlayerForm(FlaskForm):
    first_name = StringField(
        "First name", validators=[Length(min=2, max=20), DataRequired()]
    )
    last_name = StringField(
        "Last name", validators=[Length(min=2, max=20), DataRequired()]
    )
    birth_date = DateField("Birth date", validators=[DataRequired()])
    position = SelectField(
        "Position", choices=positions_choices, validators=[DataRequired()]
    )
    number = IntegerField("Number", validators=[DataRequired()])
    old_number = HiddenField()
    submit = SubmitField()

    def validate_number(self, number_to_check):
        number = Profile.query.filter_by(number=number_to_check.data).first()
        if number and (str(number_to_check.data) != self.old_number.data):
            raise ValidationError(f"Player {number.first_name} {number.last_name} already has this number!")


class CreatePlayerForm(PlayerForm):
    email_address = StringField(
        "Email address", validators=[Length(min=2, max=40), DataRequired(), Email()]
    )

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(
            email_address=email_address_to_check.data
        ).first()
        if email_address:
            raise ValidationError("Email address already exists!")


class MeetingForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    hour = TimeField("Hour", validators=[DataRequired()])
    type = SelectField("Type", choices=type_choices, validators=[DataRequired()])
    locality = StringField(
        "Locality", validators=[Length(min=2, max=20), DataRequired()]
    )
    pitch = SelectField("Pitch", choices=pitch_choices, validators=[DataRequired()])
    submit = SubmitField()


class UpdateAttendanceForm(FlaskForm):
    submit = SubmitField("Present")


class DeleteForm(FlaskForm):
    delete_obj_id = HiddenField()
    submit = SubmitField("Confirm")


class LikeForm(FlaskForm):
    player_id = HiddenField()
    meeting_id = HiddenField()
    submit = SubmitField("Present")


class ForgotPasswordForm(FlaskForm):
    email_address = StringField(
        "Email address", validators=[Length(min=2, max=40), DataRequired(), Email()]
    )
    submit = SubmitField("Send Email")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Old password", validators=[DataRequired()]
    )
    new_password = PasswordField(
        "New password", validators=[Length(min=2, max=40), DataRequired()]
    )
    confirm_password = PasswordField(
        "Confirm new password", validators=[EqualTo('new_password', message='Passwords must match!')]
    )
    submit_change = SubmitField("Change Password")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New password", validators=[Length(min=2, max=40), DataRequired()]
    )
    confirm_password = PasswordField(
        "Confirm new password", validators=[EqualTo('new_password', message='Passwords must match!')]
    )
    submit = SubmitField("Change Password")


class AvatarForm(FlaskForm):
    avatar = FileField("Avatar")
    submit_avatar = SubmitField("Change Avatar")


def form_errors(*args):
    for arg in args:
        if arg.errors != {}:
            for err_msg in arg.errors.values():
                flash(f"{err_msg[0]}", category="danger")
