from flask import Blueprint, redirect, url_for, session
from forms import Login

val = Blueprint('val', __name__)

@val.route('/login/validate', methods=['POST'])
def login_validation():
    return redirect(url_for('views.home'))