from flask import flash, redirect, flash, url_for, session
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import model
from typing import List, Type
from functools import wraps

bcrypt = Bcrypt()
csrf = CSRFProtect()

def flash_messages(form_errors: List[Type[tuple]]):
    for field, errors in form_errors.items:
        for e in errors:
            flash(f'Erro no campo {field} - {e}')

def login_required(func):
    '''
    Decorator que define que uma rota que necessita de login para receber uma request.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if'logged_user' not in session.keys() or session['logged_user'] is None:
            flash('Página inacessível enquanto o usuário não estiver logado.')
            return redirect(url_for('login.render_page'))
        return func(*args, **kwargs)
    return wrapper

def adm_required(func):
    '''
    Decorator que define uma rota que necessita que o usuário seja um administrador para receber uma request.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_role' not in session.keys() and session['user_role'] not in ['master', 'admin']:
            flash('Usuário necessita de um cargo administrativo para acessar essa página.')
            return redirect(url_for())
        return func(*args, **kwargs)
    return wrapper