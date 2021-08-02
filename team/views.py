from flask import Blueprint, render_template
from team.models import usertype_required

views = Blueprint('views', __name__, url_prefix='/')


@views.route('/')
@views.route('/home')
def home_page():
    return render_template('views/home.html')


@views.route('/squad')
def squad_page():
    return render_template('views/squad.html')


@views.route('/attendance')
def attendance_page():
    return render_template('views/attendance.html')


@views.route('/player')
def player_profile_page():
    return render_template('views/player_profile.html')


@views.route('/change-attendance')
@usertype_required('coach')
def change_attendance_page():
    return render_template('views/change_attendance.html')


@views.route('/create-meeting')
@usertype_required('coach')
def create_meeting_page():
    return render_template('views/create_meeting.html')