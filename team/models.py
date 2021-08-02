from team import db
from flask_login import UserMixin, current_user
from functools import wraps


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.String(10), default="player")
    profile = db.relationship('PlayerProfile', backref='owner')

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
    position = db.Column(db.String(3))
    number = db.Column(db.String(2), unique=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    meeting_attendance = db.relationship('Meeting',
                                         secondary=attendance,
                                         backref='present',
                                         lazy='dynamic')


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    attend = db.relationship('PlayerProfile', secondary=attendance, backref='present_players')


def usertype_required(user_type):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.user_type != user_type:
                # Redirect the user to an unauthorized notice!
                return "You are not authorized to access this page"
            return f(*args, **kwargs)

        return wrapped

    return wrapper
