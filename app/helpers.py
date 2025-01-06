from flask import flash, redirect, url_for, session, request
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import model
from functools import wraps
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
csrf = CSRFProtect()

def get_object(model: model, **kwargs):
    obj = model.query.filter(kwargs).first()
    if not obj:
        flash(f'{model.__name__} não encontrado.')
        return None
    return obj

def login_required(func):
    '''
    Decorator que define que uma página que necessita de login para receber uma request.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if'logged_user' not in session.keys() or session['logged_user'] is None:
            flash('Página inacessível enquanto o usuário não estiver logado.')
            return redirect(url_for('views.login'))
        return func(*args, **kwargs)
    return wrapper