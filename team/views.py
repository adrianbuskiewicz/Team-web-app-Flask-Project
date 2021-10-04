from flask import Blueprint, render_template, url_for, request, redirect
from team.models import Profile, Meeting, add_to_table
from flask_login import login_required
from team.dates import today, start_of_week, end_of_week, weekdays_tuple
from team.forms import LikeForm, pitch_positions
from team import db

views = Blueprint("views", __name__, url_prefix="/")


@views.route("/", methods=["GET", "POST"])
@views.route("/home", methods=["GET", "POST"])
@login_required
def home_page():
    meetings = Meeting.query.order_by(Meeting.date).filter(Meeting.date.between(start_of_week, end_of_week))
    all_players = Profile.query.all()
    present_form = LikeForm()
    absent_form = LikeForm()
    undo_form = LikeForm()

    return render_template(
        "views/home.html",
        meetings=meetings,
        weekdays=weekdays_tuple,
        present_form=present_form,
        absent_form=absent_form,
        undo_form=undo_form,
        all_players=all_players,
    )


@views.route("/home/present-like", methods=["POST"])
@login_required
def present_like():
    present_form = LikeForm()
    if present_form.submit.data:
        meeting_id = present_form.meeting_id.data
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        add_to_table(
            record_id=present_form.player_id.data,
            model=Profile,
            meeting=meeting,
            table="present_players",
            obj_id="user_id",
        )
        return redirect(url_for("views.home_page"))
    return redirect(url_for("views.home_page"))


@views.route("/home/absent-like", methods=["POST"])
@login_required
def absent_like():
    absent_form = LikeForm()
    if absent_form.submit.data:
        meeting_id = absent_form.meeting_id.data
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        add_to_table(
            record_id=absent_form.player_id.data,
            model=Profile,
            meeting=meeting,
            table="absent_players",
            obj_id="user_id",
        )
        return redirect(url_for("views.home_page"))
    return redirect(url_for("views.home_page"))


@views.route("/home/undo-like", methods=["POST"])
@login_required
def undo_like():
    undo_form = LikeForm()
    if undo_form.submit.data:
        meeting_id = undo_form.meeting_id.data
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        player_id = undo_form.player_id.data
        player_to_del = Profile.query.filter_by(user_id=player_id).first()
        if meeting.present_players.filter_by(profile_id=player_to_del.profile_id).first():
            meeting.present_players.remove(player_to_del)
            db.session.commit()
            return redirect(url_for("views.home_page"))
        elif meeting.absent_players.filter_by(profile_id=player_to_del.profile_id).first():
            meeting.absent_players.remove(player_to_del)
            db.session.commit()
            return redirect(url_for("views.home_page"))
    return redirect(url_for("views.home_page"))


@views.route("/squad", methods=["GET", "POST"])
@login_required
def squad_page():
    players = Profile.query.all()
    if request.method == "POST":
        return redirect(url_for("player_profile_page"))
    else:
        return render_template("views/squad.html", positions=pitch_positions, players=players)


@views.route("/schedule")
@login_required
def schedule_page():
    meetings = Meeting.query.filter(Meeting.date > end_of_week).order_by(Meeting.date)
    return render_template("views/schedule.html", meetings=meetings)


@views.route("/attendance")
@login_required
def attendance_page():
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date)
    players = Profile.query.order_by(Profile.last_name).all()
    return render_template(
        "views/attendance.html",
        meetings=meetings,
        players=players,
        positions=pitch_positions,
    )


@views.route("/attendance/<meeting_id>")
@login_required
def meeting_attendance_page(meeting_id):
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    present_players = meeting.attendance.all()
    absent_players = tuple(player for player in Profile.query.all() if player not in present_players)
    return render_template(
        "views/meeting_attendance.html",
        positions=pitch_positions,
        meeting=meeting,
        present_players=present_players,
        absent_players=absent_players,
    )


@views.route("/profile/<player_id>")
@login_required
def player_profile_page(player_id):
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date.desc())
    player = Profile.query.filter_by(profile_id=player_id).first()

    if player.birth_date:
        age_in_days = today - player.birth_date
        age = int(age_in_days.days / 365.2425)
    else:
        age = None

    how_many_present = len(tuple([1 for meeting in meetings if player in meeting.attendance]))
    attendance_percentage = f"{how_many_present / len(tuple(meetings)):.0%}" if any(meetings) else None
    return render_template(
        "views/player_profile.html",
        attendance_percentage=attendance_percentage,
        age=age,
        player=player,
        meetings=meetings,
    )
