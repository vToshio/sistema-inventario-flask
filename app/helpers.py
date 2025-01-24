from flask import flash, redirect, flash, url_for, session
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from typing import List, Dict
from functools import wraps
import random as r
import string

bcrypt = Bcrypt()
csrf = CSRFProtect()

def generate_random_password(length:int=16) -> str:
    '''
    Função auxiliar que gera uma senha aleatória contendo simbolos, letras maiúsculas ou minúsculas e dígitos numéricos.

    Argumentos:
    - lenght: define o tamanho da senha, com valor padrão 16.
    '''

    if (length > 100 or length<10):
        raise Exception('A senha precisa tem entre 10 a 100 caracteres.')

    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    signals = '!@#$%&*-+='
    digits = '0123456789'
    characters = [upper, lower, signals, digits]

    password = ''
    last = -1
    for _ in range(length):
        num = r.randint(0,3) 
        if num == last:
            if num < 1: 
                num = num + r.randint(1, 3)
            elif num > 3: 
                num = num - r.randint(0, 2)
        
        new_char = characters[num][r.randint(0, len(characters[num])-1)]
        password += new_char

    return password


def flash_messages(form_errors: Dict[str, List[str]]):
    '''
    Função auxiliar e exibe notificações de erro de preenchimento em um campo
    '''
    for field, errors in form_errors.items():
        for e in errors:
            flash(f'Erro no campo {field} - {e}')

def login_required(func):
    '''
    Decorator que define que uma rota que necessita de login para receber uma request.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session.keys() or not session['logged_in']:
            flash('Página inacessível enquanto o usuário não estiver logado.')
            return redirect(url_for('login.render_page'))
        return func(*args, **kwargs)
    return wrapper

def adm_required(route:str='home.render_page'):
    '''
    Decorator que define uma rota que necessita que o usuário seja um administrador para receber uma request.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_role' in session.keys() and session['user_role'] not in ['master', 'admin']:
                flash('Usuário necessita de um cargo administrativo para acessar essa página.')
                return redirect(url_for(route))
            return func(*args, **kwargs)
        return wrapper
    return decorator