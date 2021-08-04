from flask import Blueprint, render_template, redirect, url_for, flash
from team.models import User, Profile, Meeting
from team.forms import AddPlayerForm, CreateMeetingForm
from team import db
from werkzeug.security import generate_password_hash
import secrets
import string

creator = Blueprint('creator', __name__, url_prefix='/')


@creator.route('/add-player', methods=['GET', 'POST'])
#@usertype_required('coach')
def add_player_page():
    add_player_form = AddPlayerForm()
    if add_player_form.validate_on_submit():
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        user_to_add = User(email_address=add_player_form.email_address.data,
                    password_hash=generate_password_hash(password))
        profile_to_add = Profile(first_name=add_player_form.first_name.data,
                              last_name=add_player_form.last_name.data,
                              position=add_player_form.position.data,
                              number=add_player_form.number.data,
                              owner=user_to_add)
        db.session.add(user_to_add)
        db.session.add(profile_to_add)
        db.session.commit()
        return redirect(url_for('creator.add_player_page'))
    if add_player_form.errors != {}:
        for err_msg in add_player_form.errors.values():
            flash(f'{err_msg[0]}', category='danger')
    return render_template('creator/add_player.html', add_player_form=add_player_form)


@creator.route('/create-meeting', methods=['GET', 'POST'])
#@usertype_required('coach')
def create_meeting_page():
    create_meeting_form = CreateMeetingForm()
    if create_meeting_form.validate_on_submit():
        meeting_to_create = Meeting(date=create_meeting_form.date.data,
                                    hour=str(create_meeting_form.hour.data)[:5],
                                    type=create_meeting_form.type.data,
                                    locality=create_meeting_form.locality.data,
                                    pitch=create_meeting_form.pitch.data)
        db.session.add(meeting_to_create)
        db.session.commit()
        return redirect(url_for('creator.create_meeting_page'))
    if create_meeting_form.errors != {}:
        for err_msg in create_meeting_form.errors.values():
            flash(f'{err_msg[0]}', category='danger')
    return render_template('creator/create_meeting.html', create_meeting_form=create_meeting_form)


@creator.route('/change-attendance')
# @usertype_required('coach')
def change_attendance_page():
    return render_template('creator/change_attendance.html')
