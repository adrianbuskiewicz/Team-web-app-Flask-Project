from team import db
from flask_login import UserMixin, current_user
from functools import wraps
from flask import flash, redirect, url_for, request


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_address = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(60))
    user_type = db.Column(db.String(10), default="player")
    profile = db.relationship('Profile', backref='owner', uselist=False)

    def is_coach(self):
        return self.user_type == 'coach'

    def get_id(self):
        return self.user_id


attendance_table = db.Table('attendance_table',
                            db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.meeting_id')),
                            db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id')),
                            )

present_likes = db.Table('present_likes',
                         db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.meeting_id')),
                         db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id')),
                         )

absent_likes = db.Table('absent_likes',
                        db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.meeting_id')),
                        db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id')),
                        )


class Profile(db.Model):
    profile_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date, default=None)
    position = db.Column(db.String(20))
    number = db.Column(db.String(2), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


class Meeting(db.Model):
    meeting_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    hour = db.Column(db.String(5))
    day = db.Column(db.String(15))
    type = db.Column(db.String(20))
    locality = db.Column(db.String(50))
    pitch = db.Column(db.String(30))
    attendance = db.relationship('Profile',
                                 secondary=attendance_table,
                                 lazy='dynamic')
    present_players = db.relationship('Profile',
                                      secondary=present_likes,
                                      lazy='dynamic')
    absent_players = db.relationship('Profile',
                                     secondary=absent_likes,
                                     lazy='dynamic')


def delete_object(request_val, model, obj_id):
    item_to_delete = request.form.get(request_val)
    del_item = model.query.filter_by(**{obj_id: item_to_delete}).first()
    if del_item:
        db.session.delete(del_item)
        db.session.commit()


def add_to_table(request_val, model, meeting, table, obj_id):
    record_id = request.form.get(request_val)
    record_to_add = model.query.filter_by(**{obj_id: record_id}).first()
    getattr(meeting, table).append(record_to_add)
    db.session.commit()


def del_from_table():
    pass


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
