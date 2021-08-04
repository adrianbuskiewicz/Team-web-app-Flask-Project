from team import db
from flask_login import UserMixin, current_user
from functools import wraps
from flask import flash, redirect, url_for


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_address = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(60))
    user_type = db.Column(db.String(10), default="player")
    profile = db.relationship('Profile', backref='owner', uselist=False)

    def is_coach(self):
        return self.user_type == 'coach'


attendance = db.Table('attendance',
                      db.Column('profile_id', db.Integer, db.ForeignKey('profile.id'), primary_key=True),
                      db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.id'), primary_key=True),
                      )


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date, default=None)
    position = db.Column(db.String(20))
    number = db.Column(db.String(2), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meeting_attendance = db.relationship('Meeting',
                                         secondary=attendance,
                                         lazy='dynamic')


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    hour = db.Column(db.String(10))
    day = db.Column(db.String(15))
    type = db.Column(db.String(20))
    locality = db.Column(db.String(50))
    pitch = db.Column(db.String(30))
    attendance = db.relationship('Profile', secondary=attendance)


def usertype_required(user_type):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.user_type != user_type:
                # Redirect the user to an unauthorized notice!
                flash("You are not a coach!")
                return redirect(url_for('views.home_page'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper
