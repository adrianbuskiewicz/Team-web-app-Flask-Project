from flask import Blueprint, render_template, url_for, request, redirect
from team.models import Profile, Meeting, add_to_table
from flask_login import login_required
from team.dates import today, start_of_week, end_of_week, weekdays_tuple
from team.forms import PresentForm, AbsentForm, UndoForm, pitch_positions
from team import db

views = Blueprint('views', __name__, url_prefix='/')


@views.route('/', methods=['GET', 'POST'])
@views.route('/home', methods=['GET', 'POST'])
@login_required
def home_page():
    meetings = Meeting.query.filter(Meeting.date >= start_of_week).filter(Meeting.date <= end_of_week).order_by(
        Meeting.date)
    present_form = PresentForm()
    absent_form = AbsentForm()
    undo_form = UndoForm()
    weekdays = weekdays_tuple

    if present_form.submit_present.data:
        meeting_id = request.form.get('meeting_id')
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        print(meeting)
        add_to_table(
            request_val='present_player',
            model=Profile,
            meeting=meeting,
            table='present_players',
            obj_id='user_id')
        return redirect(url_for('views.home_page'))

    if absent_form.submit_absent.data:
        meeting_id = request.form.get('meeting_id')
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        print(meeting)
        add_to_table(
            request_val='absent_player',
            model=Profile,
            meeting=meeting,
            table='absent_players',
            obj_id='user_id')
        return redirect(url_for('views.home_page'))

    if undo_form.submit_undo.data:
        meeting_id = request.form.get('meeting_id')
        meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
        record_id = request.form.get('undo_player')
        record_to_del = Profile.query.filter_by(user_id=record_id).first()
        if meeting.present_players.filter_by(profile_id=record_id).first():
            meeting.present_players.remove(record_to_del)
            db.session.commit()
            return redirect(url_for('views.home_page'))
        if meeting.absent_players.filter_by(profile_id=record_id).first():
            meeting.absent_players.remove(record_to_del)
            db.session.commit()
            return redirect(url_for('views.home_page'))

    return render_template('views/home.html',
                           meetings=meetings,
                           weekdays=weekdays,
                           present_form=present_form,
                           absent_form=absent_form,
                           undo_form=undo_form)


@views.route('/squad', methods=['GET', 'POST'])
@login_required
def squad_page():
    positions = pitch_positions
    players = Profile.query.all()

    if request.method == 'POST':
        return redirect(url_for('player_profile_page'))
    else:
        return render_template('views/squad.html',
                               positions=positions,
                               players=players)


@views.route('/schedule')
@login_required
def schedule_page():
    meetings = Meeting.query.filter(Meeting.date > end_of_week).order_by(Meeting.date)
    return render_template('views/schedule.html',
                           meetings=meetings)


@views.route('/attendance')
@login_required
def attendance_page():
    positions = pitch_positions
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date)
    players = Profile.query.order_by(Profile.last_name).all()
    return render_template('views/attendance.html',
                           meetings=meetings,
                           players=players,
                           positions=positions)


@views.route('/attendance/<meeting_id>')
@login_required
def meeting_attendance_page(meeting_id):
    positions = pitch_positions
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    present_players = meeting.attendance.all()
    absent_players = (player for player in Profile.query.all() if player not in present_players)
    return render_template('views/meeting_attendance.html',
                           positions=positions,
                           meeting=meeting,
                           present_players=present_players,
                           absent_players=absent_players)


@views.route('/profile/<player_id>')
@login_required
def player_profile_page(player_id):
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date.desc())
    player = Profile.query.filter_by(profile_id=player_id).first()
    age_in_days = today - player.birth_date if player.birth_date else None
    age = int(age_in_days.days / 365.2425) if age_in_days else None
    how_many_present = len(tuple([1 for meeting in meetings if player in meeting.attendance]))
    how_many_meetings = len(tuple(meetings))
    attendance_percentage = f"{how_many_present / how_many_meetings:.0%}"
    return render_template('views/player_profile.html',
                           attendance_percentage=attendance_percentage,
                           age=age,
                           player=player,
                           meetings=meetings)
