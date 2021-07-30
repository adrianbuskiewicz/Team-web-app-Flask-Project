from flask import Blueprint, render_template, redirect, url_for, flash
from team.models import User
from team.forms import CreateUserForm
from team import db


auth = Blueprint('auth', __name__, url_prefix='/')


@auth.route('/login')
def login_page():
    return render_template('base.html')


@auth.route('/create', methods=['GET', 'POST'])
def create_user_page():
    create_form = CreateUserForm()
    if create_form.validate_on_submit():
        user = User(email_address=create_form.email_address.data,
                    first_name=create_form.first_name.data,
                    last_name=create_form.last_name.data,
                    position=create_form.position.data,
                    specified_position=create_form.specified_position)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('create_user_page'))
    return render_template('auth/create.html', create_form=create_form)
