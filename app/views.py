from flask import Blueprint, render_template, redirect, url_for, session
from forms import Login

views = Blueprint('views', __name__)

@views.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', next=url_for('views.home') ,form=Login())

@views.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', pagetitle='Home')