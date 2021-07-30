from team import db
from flask_login import UserMixin


class Player(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(60))
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    birth_date = db.Column(db.Date)
    position = db.Column(db.String(3))


class Coach(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(60), unique=True)
    token = db.Column(db.String(4))
    password_hash = db.Column(db.String(60))






