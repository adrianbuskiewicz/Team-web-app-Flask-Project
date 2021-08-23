import os
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"

mail = Mail()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_NAME}",
        MAIL_SERVER='smtp.mailtrap.io',
        MAIL_PORT=2525,
        MAIL_USERNAME='3ed64a2c3a31da',
        MAIL_PASSWORD='8cfbd4b9483388',
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAX_CONTENT_LENGTH=1024*1024,
        UPLOAD_EXTENSIONS=['.jpg', '.png'],
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login_page"
    login_manager.init_app(app)

    from team.auth import auth
    from team.views import views
    from team.creator import creator

    app.register_blueprint(auth)
    app.register_blueprint(views)
    app.register_blueprint(creator)

    from team.models import User, Profile

    create_database(app.instance_path, app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_first_request
    def create_coach_user():
        if not User.query.filter_by(email_address='coach@wp.pl').first():
            coach_user = User(
                email_address='coach@wp.pl',
                password_hash=generate_password_hash('coach'),
                user_type='coach',
            )
            db.session.add(coach_user)
            db.session.commit()

    return app


def create_database(app_path, app):
    if not os.path.exists(f"{app_path}/{DB_NAME}"):
        db.create_all(app=app)
