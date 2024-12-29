from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages, session
from forms import Login

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def root():
    if 'logged_user' in session.keys() and session['logged_user'] is not None:
        return redirect(url_for('views.home'))
    return redirect(url_for('views.login', next=url_for('views.home')))

@views.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', next=url_for('val.login_validation'), form=Login(), messages=get_flashed_messages(with_categories=True))

@views.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_user', None)
    return redirect(url_for('views.login', next=url_for('views.home')))

@views.route('/home', methods=['GET', 'POST'])
def home():
    if 'logged_user' in session.keys() and session['logged_user'] is not None:
        return render_template('home.html', pagetitle='Home')
    flash('Página inacessível enquanto o usuário não estiver logado.', 'error')
    return redirect(url_for('views.login'))