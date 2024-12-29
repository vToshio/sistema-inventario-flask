from flask import Blueprint, redirect, url_for, flash, request, session
from flask_bcrypt import Bcrypt
from models import User

val = Blueprint('val', __name__)
bcrypt = Bcrypt()

@val.route('/login/validate', methods=['POST'])
def login_validation():
    next = request.form['nextpage']
    username = request.form['username']
    passwd = request.form['password']
    
    found_user = User.query.filter(User.username == username).first()
    if found_user:
        if bcrypt.check_password_hash(found_user.password, passwd):
            session['logged_user'] = username
            return redirect(url_for('views.home'))
        flash('Senha incorreta.', 'error')
    else:
        flash('Usuário ainda não cadastrado.', 'error')
    return redirect(url_for('views.login', next=next))