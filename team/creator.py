from flask import Blueprint, render_template, redirect, url_for, flash, request
from team.models import (
    User,
    Profile,
    Meeting,
    usertype_required,
    delete_object,
)
from team.forms import (
    AddPlayerForm,
    CreateMeetingForm,
    UpdatePlayerForm,
    UpdateMeetingForm,
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

creator = Blueprint("creator", __name__, url_prefix="/")


@creator.route("/players", methods=["GET", "POST"])
@login_required
@usertype_required('coach')
def players_page():
    players = User.query.filter_by(user_type="player")
    add_player_form = AddPlayerForm()

    if add_player_form.submit_create.data and add_player_form.validate():
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(8))
        user_to_add = User(
            email_address=add_player_form.email_address.data,
            password_hash=generate_password_hash(password),
        )
        profile_to_add = Profile(
            avatar='default.png',
            first_name=add_player_form.first_name.data,
            last_name=add_player_form.last_name.data,
            position=add_player_form.position.data,
            number=add_player_form.number.data,
            birth_date=add_player_form.birth_date.data,
            owner=user_to_add,
        )
        db.session.add(user_to_add)
        db.session.add(profile_to_add)
        db.session.commit()
        # msg = Message('Team web app - Your account was created!',
        #               sender='team@mailtrap.io',
        #               recipients=[user_to_add.email_address])
        # msg.body = f"Hey, we created an account for you!\nIt's your password: {password}\nYou can change it in " \
        #            f"account settings! "
        # mail.send(msg)
        flash("Player created!", category="info")
        return redirect(url_for("creator.players_page"))

    update_player_form = UpdatePlayerForm()

    if update_player_form.submit_update.data:
        profile_to_update = request.form.get("update_player")
        update_profile = Profile.query.filter_by(profile_id=profile_to_update).first()
        if update_profile:
            update_profile.first_name = update_player_form.first_name.data
            update_profile.last_name = update_player_form.last_name.data
            update_profile.position = update_player_form.position.data
            update_profile.number = update_player_form.number.data
            update_profile.birth_date = update_player_form.birth_date.data
            db.session.commit()
            flash("Changed player!", category="info")
            return redirect(url_for("creator.players_page"))

    delete_player_form = DeleteForm()

    if delete_player_form.submit_delete.data and delete_player_form.validate():
        delete_object(request_val="delete_player", model=Profile, obj_id="user_id")
        delete_object(request_val="delete_player", model=User, obj_id="user_id")
        flash("Deleted player!", category="info")
        return redirect(url_for("creator.players_page"))

    form_errors(add_player_form)

    return render_template(
        "creator/players.html",
        add_player_form=add_player_form,
        update_form=update_player_form,
        delete_form=delete_player_form,
        players=players,
        positions=pitch_positions,
    )


@creator.route("/meetings", methods=["GET", "POST"])
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
        ("Past meetings", past_meetings)
    )
    create_meeting_form = CreateMeetingForm()

    if create_meeting_form.submit_create.data and create_meeting_form.validate():
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
        return redirect(url_for("creator.meetings_page"))

    update_meeting_form = UpdateMeetingForm()

    if update_meeting_form.submit_update.data:
        update_id = request.form.get("update_meeting")
        meeting_to_update = Meeting.query.filter_by(meeting_id=update_id).first()
        if meeting_to_update:
            meeting_to_update.date = update_meeting_form.date.data
            meeting_to_update.hour = str(update_meeting_form.hour.data)[:5]
            meeting_to_update.day = weekdays_tuple[create_meeting_form.date.data.weekday()]
            meeting_to_update.locality = update_meeting_form.locality.data
            meeting_to_update.type = update_meeting_form.type.data
            meeting_to_update.pitch = update_meeting_form.pitch.data
            db.session.commit()
            flash("Changed meeting!", category="info")
            return redirect(url_for("creator.meetings_page"))

    delete_meeting_form = DeleteForm()

    if delete_meeting_form.submit_delete.data and delete_meeting_form.validate():
        delete_object(request_val="delete_meeting", model=Meeting, obj_id="meeting_id")
        flash("Deleted meeting!", category="info")
        return redirect(url_for("creator.meetings_page"))

    form_errors(create_meeting_form)

    return render_template(
        "creator/meetings.html",
        create_meeting_form=create_meeting_form,
        update_form=update_meeting_form,
        delete_form=delete_meeting_form,
        meetings_list=meetings_list,
    )


@creator.route("/attendance/update/<meeting_id>", methods=["GET", "POST"])
@login_required
@usertype_required("coach")
def update_attendance_page(meeting_id):
    update_attendance_form = UpdateAttendanceForm()
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    players = Profile.query.all()
    if update_attendance_form.submit_update.data:
        player_present_id = request.form.get("present_player")
        player_present = Profile.query.filter_by(profile_id=player_present_id).first()
        if meeting.attendance.filter_by(profile_id=player_present_id).first():
            meeting.attendance.remove(player_present)
            db.session.commit()
        else:
            meeting.attendance.append(player_present)
            db.session.commit()
        return redirect(url_for("creator.update_attendance_page", meeting_id=meeting.meeting_id))

    return render_template(
        "creator/attendance_update.html",
        update_attendance_form=update_attendance_form,
        meeting=meeting,
        players=players,
        positions=pitch_positions,
    )
