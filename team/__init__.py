import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = 'database.db'


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_NAME}"
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from team.auth import auth

    app.register_blueprint(auth)

    create_database(app.instance_path, app)

    return app


def create_database(app_path, app):
    if not os.path.exists(f"{app_path}/{DB_NAME}"):
        db.create_all(app=app)
