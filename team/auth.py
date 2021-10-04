from flask import Blueprint, render_template, redirect, url_for, flash, abort
from team.models import User
from team.forms import LoginForm, ForgotPasswordForm, ChangePasswordForm, ResetPasswordForm, AvatarForm, form_errors
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from team import mail
from flask_mail import Message
from team import db
import os


auth = Blueprint("auth", __name__, url_prefix="/")


@auth.route("/login", methods=["GET", "POST"])
def login_page():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_to_check = User.query.filter_by(email_address=login_form.email_address.data).first()
        if user_to_check:
            if check_password_hash(user_to_check.password_hash, login_form.password.data):
                login_user(user_to_check)
                flash("You are logged in!", category="success")
                return redirect(url_for("views.home_page"))
            else:
                flash("Wrong password!", category="danger")
        else:
            flash("Wrong email!", category="danger")
    return render_template("auth/login.html", login_form=login_form)


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout_page():
    logout_user()
    flash("You were logged out!", category="danger")
    return redirect(url_for("auth.login_page"))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_page():
    forgot_password_form = ForgotPasswordForm()

    if forgot_password_form.validate_on_submit():
        user_to_check = User.query.filter_by(email_address=forgot_password_form.email_address.data).first()
        if user_to_check:
            token = user_to_check.get_reset_token()
            msg = Message("Team web app - Reset your password!",
                          sender='team@mailtrap.io',
                          recipients=[user_to_check.email_address])
            msg.body = f'''To reset your password, visit the following link: 
            {url_for('auth.reset_password_page', token=token, _external=True)}
                        
                        If you did not make this request then simply ignore this email and no changes will be made.
                        '''
            mail.send(msg)
            return redirect(url_for('auth.login_page'))
        else:
            flash("User with given email address doesn't exist!", category='danger')

    form_errors(forgot_password_form)
    return render_template("auth/forgot_password.html", forgot_password_form=forgot_password_form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_page(token):
    reset_password_form = ResetPasswordForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token!', category='danger')
        return redirect(url_for('auth.forgot_password_page'))

    if reset_password_form.validate_on_submit():
        user.password_hash = generate_password_hash(reset_password_form.new_password.data)
        db.session.commit()
        flash('Your successfully reset your password! Now you can log in!', category='success')
        return redirect(url_for('auth.login_page'))

    return render_template('auth/reset_password.html', reset_password_form=reset_password_form)


@auth.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    avatar_form = AvatarForm()

    if avatar_form.submit_avatar.data and avatar_form.validate():
        if avatar_form.avatar.data:
            filename = secure_filename(avatar_form.avatar.data.filename)
            file_ext = os.path.splitext(filename)[1]
            basedir = os.path.abspath(os.path.dirname(__file__)) + '/static/avatars/'
            old_avatar = f"{basedir}{current_user.profile.avatar}"
            avatar_name = f"{current_user.profile.first_name[0]}" \
                          f"{current_user.profile.last_name[0]}" \
                          f"{1000-current_user.profile.user_id}"
            if file_ext in ['.jpg', '.png']:
                os.remove(old_avatar) if current_user.profile.avatar != 'default.png' else None
                avatar_form.avatar.data.save(basedir + avatar_name + file_ext)
                current_user.profile.avatar = avatar_name + file_ext
                db.session.commit()
                return redirect(url_for('auth.settings_page'))

    change_password_form = ChangePasswordForm()

    if change_password_form.submit_change.data and change_password_form.validate():
        user_to_check = User.query.filter_by(email_address=current_user.email_address).first()
        if check_password_hash(user_to_check.password_hash, change_password_form.old_password.data):
            user_to_check.password_hash = generate_password_hash(change_password_form.new_password.data)
            db.session.commit()
            flash("Successfully updated your password!", category='success')
        else:
            flash("Wrong old password", category='danger')

    form_errors(change_password_form, avatar_form)
    return render_template("auth/settings.html",
                           avatar_form=avatar_form,
                           change_password_form=change_password_form)
