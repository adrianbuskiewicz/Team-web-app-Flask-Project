from flask import Blueprint, render_template, redirect, url_for, flash
from team.models import User
from team.forms import LoginForm
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user

auth = Blueprint('auth', __name__, url_prefix='/')


@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_to_check = User.query.filter_by(email_address=login_form.email_address.data).first()
        if user_to_check:
            if check_password_hash(user_to_check.password_hash, login_form.password.data):
                login_user(user_to_check, remember=True)
                flash('You are logged in!', category='success')
                return redirect(url_for('views.home_page'))
            else:
                flash("Wrong password!", category='danger')
        else:
            flash("Wrong email!", category='danger')
    return render_template('auth/login.html', login_form=login_form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout_page():
    logout_user()
    flash("You were logged out!", category='error')
    return redirect(url_for('auth.login_page'))

