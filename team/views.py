from flask import Blueprint, render_template, url_for, request, redirect
from team.models import Profile, Meeting
from flask_login import login_required
from team.dates import today, start_of_week, end_of_week, weekdays_tuple

views = Blueprint('views', __name__, url_prefix='/')


@views.route('/')
@views.route('/home')
@login_required
def home_page():
    weekdays = weekdays_tuple
    meetings = Meeting.query.filter(Meeting.date >= start_of_week).filter(Meeting.date <= end_of_week).order_by(Meeting.date)
    return render_template('views/home.html', meetings=meetings, weekdays=weekdays)


@views.route('/squad', methods=['GET', 'POST'])
@login_required
def squad_page():
    positions = ('goalkeeper',
                 'defender',
                 'midfielder',
                 'forward')
    players = Profile.query.all()
    if request.method == 'POST':
        return redirect(url_for('player_profile_page'))
    else:
        return render_template('views/squad.html', positions=positions, players=players)


@views.route('/schedule')
@login_required
def schedule_page():
    meetings = Meeting.query.filter(Meeting.date > end_of_week).order_by(Meeting.date)
    return render_template('views/schedule.html', meetings=meetings)


@views.route('/attendance')
@login_required
def attendance_page():
    positions = ('goalkeeper',
                 'defender',
                 'midfielder',
                 'forward')
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date)
    players = Profile.query.order_by(Profile.last_name).all()
    return render_template('views/attendance.html', meetings=meetings, players=players, positions=positions)


@views.route('/attendance/<meeting_id>')
@login_required
def meeting_attendance_page(meeting_id):
    positions = ('goalkeeper',
                 'defender',
                 'midfielder',
                 'forward')
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    players = Profile.query.all()
    return render_template('views/meeting_attendance.html', meeting=meeting, players=players)


@views.route('/profile/<player_id>')
@login_required
def player_profile_page(player_id):
    meetings = Meeting.query.filter(Meeting.date < today).order_by(Meeting.date)
    player = Profile.query.filter_by(profile_id=player_id).first()
    return render_template('views/player_profile.html', player=player, meetings=meetings)




