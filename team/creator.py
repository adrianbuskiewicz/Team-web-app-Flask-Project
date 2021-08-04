from flask import Blueprint, render_template, redirect, url_for, flash
from team.models import User, Profile, Meeting, usertype_required
from team.forms import AddPlayerForm, CreateMeetingForm, form_errors
from team import db
from flask_login import login_required
from werkzeug.security import generate_password_hash
from team.dates import weekdays_tuple
import secrets
import string

creator = Blueprint('creator', __name__, url_prefix='/')


@creator.route('/players', methods=['GET', 'POST'])
def players_page():
    players = Profile.query.all()
    add_player_form = AddPlayerForm()
    update_form = AddPlayerForm()
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
        print(password)
        db.session.commit()
        flash("User created successfully!")
        return redirect(url_for('creator.players_page'))
    form_errors(add_player_form)
    return render_template('creator/players.html',
                           add_player_form=add_player_form,
                           update_form=update_form,
                           players=players)


@creator.route('/meetings', methods=['GET', 'POST'])
@login_required
@usertype_required('player')
def meetings_page():
    meetings = Meeting.query.order_by(Meeting.date).all()
    create_meeting_form = CreateMeetingForm()
    update_form = CreateMeetingForm()
    if create_meeting_form.validate_on_submit():
        meeting_to_create = Meeting(date=create_meeting_form.date.data,
                                    hour=str(create_meeting_form.hour.data)[:5],
                                    day=weekdays_tuple[create_meeting_form.date.data.weekday()],
                                    type=create_meeting_form.type.data,
                                    locality=create_meeting_form.locality.data,
                                    pitch=create_meeting_form.pitch.data)
        db.session.add(meeting_to_create)
        db.session.commit()
        flash("Meeting created successfully!")
        return redirect(url_for('creator.meetings_page'))
    form_errors(create_meeting_form)
    return render_template('creator/meetings.html',
                           create_meeting_form=create_meeting_form,
                           update_form=update_form,
                           meetings=meetings)
