from flask import Blueprint, render_template


views = Blueprint('views', __name__, url_prefix='/')


@views.route('/')
@views.route('/home')
def home_page():
    return render_template('views/home.html')