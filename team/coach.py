from flask import Blueprint, render_template, redirect, url_for, flash, request
from team.models import (
    User,
    Profile,
    Meeting,
    usertype_required,
    delete_object,
)
from team.forms import (
    CreatePlayerForm,
    PlayerForm,
    MeetingForm,
    UpdateAttendanceForm,
    DeleteForm,
    form_errors,
    pitch_positions,
)
from team import db, mail
from flask_mail import Message
from flask_login import login_required
from werkzeug.security import generate_password_hash
from team.dates import weekdays_tuple, start_of_week, end_of_week
import secrets
import string


coach = Blueprint("coach", __name__, url_prefix="/")


@coach.route("/players")
@login_required
@usertype_required('coach')
def players_page():
    players = User.query.filter_by(user_type="player")
    create_player_form = CreatePlayerForm()
    update_player_form = PlayerForm()
    delete_player_form = DeleteForm()
    return render_template(
        "coach/players.html",
        create_player_form=create_player_form,
        update_player_form=update_player_form,
        delete_player_form=delete_player_form,
        players=players,
        positions=pitch_positions,
    )


@coach.route("/players/create-player", methods=['POST'])
@login_required
@usertype_required('coach')
def create_player():
    create_player_form = CreatePlayerForm()
    if create_player_form.validate_on_submit():
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(8))
        user_to_create = User(
            email_address=create_player_form.email_address.data,
            password_hash=generate_password_hash(password),
        )
        profile_to_create = Profile(
            avatar='default.png',
            first_name=create_player_form.first_name.data,
            last_name=create_player_form.last_name.data,
            position=create_player_form.position.data,
            number=create_player_form.number.data,
            birth_date=create_player_form.birth_date.data,
            owner=user_to_create,
        )
        db.session.add(user_to_create)
        db.session.add(profile_to_create)
        db.session.commit()
        msg = Message('Team web app - Your account was created!',
                      sender='team2@mailtrap.io',
                      recipients=[user_to_create.email_address])
        msg.body = f"Hey, we created an account for you!\nIt's your password: {password}\nYou can change it in " \
                   f"account settings! "
        mail.send(msg)
        flash("Player created!", category="info")
        return redirect(url_for("coach.players_page"))
    form_errors(create_player_form)
    return redirect(url_for("coach.players_page"))


@coach.route("/players/update-player", methods=['POST'])
@login_required
@usertype_required('coach')
def update_player():
    update_player_form = PlayerForm()
    if update_player_form.validate_on_submit():
        profile_to_update = request.form.get("update_player")
        update_profile = Profile.query.filter_by(profile_id=profile_to_update).first()
        if update_profile:
            update_profile.first_name = update_player_form.first_name.data
            update_profile.last_name = update_player_form.last_name.data
            update_profile.position = update_player_form.position.data
            update_profile.birth_date = update_player_form.birth_date.data
            update_profile.number = update_player_form.number.data
            db.session.commit()
            flash("Changed player!", category="info")
            return redirect(url_for("coach.players_page"))
    form_errors(update_player_form)
    return redirect(url_for("coach.players_page"))


@coach.route("/players/delete-player", methods=['POST'])
@login_required
@usertype_required('coach')
def delete_player():
    delete_player_form = DeleteForm()
    delete_object(item_to_delete=delete_player_form.delete_obj_id.data, model=Profile, obj_id="user_id")
    delete_object(item_to_delete=delete_player_form.delete_obj_id.data, model=User, obj_id="user_id")
    flash("Deleted player!", category="info")
    return redirect(url_for("coach.players_page"))


@coach.route("/meetings")
@login_required
@usertype_required("coach")
def meetings_page():
    meetings = Meeting.query.order_by(Meeting.date.desc())
    future_meetings = meetings.filter(Meeting.date > end_of_week)
    this_week_meetings = meetings.filter(Meeting.date.between(start_of_week, end_of_week))
    past_meetings = meetings.filter(Meeting.date < start_of_week)
    meetings_list = (
        ("Future meetings", future_meetings),
        ("Current week meetings", this_week_meetings),
        ("Past meetings", past_meetings),
    )
    create_meeting_form = MeetingForm()
    update_meeting_form = MeetingForm()
    delete_meeting_form = DeleteForm()

    return render_template(
        "coach/meetings.html",
        create_meeting_form=create_meeting_form,
        update_meeting_form=update_meeting_form,
        delete_meeting_form=delete_meeting_form,
        meetings_list=meetings_list,
    )


@coach.route('/meetings/create-meeting', methods=['POST'])
@login_required
@usertype_required("coach")
def create_meeting():
    create_meeting_form = MeetingForm()
    if create_meeting_form.validate_on_submit():
        meeting_to_create = Meeting(
            date=create_meeting_form.date.data,
            hour=str(create_meeting_form.hour.data)[:5],
            day=weekdays_tuple[create_meeting_form.date.data.weekday()],
            type=create_meeting_form.type.data,
            locality=create_meeting_form.locality.data,
            pitch=create_meeting_form.pitch.data,
        )
        db.session.add(meeting_to_create)
        db.session.commit()
        flash("Meeting created!", category="info")
        return redirect(url_for("coach.meetings_page"))


@coach.route('/meetings/update-meeting', methods=['POST'])
@login_required
@usertype_required("coach")
def update_meeting():
    update_meeting_form = MeetingForm()
    if update_meeting_form.validate_on_submit():
        update_id = request.form.get("update_meeting")
        meeting_to_update = Meeting.query.filter_by(meeting_id=update_id).first()
        if meeting_to_update:
            meeting_to_update.date = update_meeting_form.date.data
            meeting_to_update.hour = str(update_meeting_form.hour.data)[:5]
            meeting_to_update.day = weekdays_tuple[update_meeting_form.date.data.weekday()]
            meeting_to_update.locality = update_meeting_form.locality.data
            meeting_to_update.type = update_meeting_form.type.data
            meeting_to_update.pitch = update_meeting_form.pitch.data
            db.session.commit()
            flash("Changed meeting!", category="info")
            return redirect(url_for("coach.meetings_page"))


@coach.route('/meetings/delete-meeting', methods=['POST'])
@login_required
@usertype_required("coach")
def delete_meeting():
    delete_meeting_form = DeleteForm()
    delete_object(item_to_delete=delete_meeting_form.delete_obj_id.data, model=Meeting, obj_id="meeting_id")
    flash("Deleted meeting!", category="info")
    return redirect(url_for("coach.meetings_page"))


@coach.route("/attendance/update/<meeting_id>", methods=["GET", "POST"])
@login_required
@usertype_required("coach")
def update_attendance_page(meeting_id):
    update_attendance_form = UpdateAttendanceForm()
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    players = Profile.query.all()
    if update_attendance_form.submit.data:
        player_present_id = request.form.get("present_player")
        player_present = Profile.query.filter_by(profile_id=player_present_id).first()
        if meeting.attendance.filter_by(profile_id=player_present_id).first():
            meeting.attendance.remove(player_present)
            db.session.commit()
        else:
            meeting.attendance.append(player_present)
            db.session.commit()
        return redirect(url_for("coach.update_attendance_page", meeting_id=meeting.meeting_id))

    return render_template(
        "coach/attendance_update.html",
        update_attendance_form=update_attendance_form,
        meeting=meeting,
        players=players,
        positions=pitch_positions,
    )
