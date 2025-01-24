from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages, session, request
from app.helpers import login_required, flash_messages, bcrypt
from app.src.login.forms import LoginForm
from app.models import *

login = Blueprint('login', __name__)

@login.route('/', methods=['GET'])
def root():
    '''
    Endpoint root, que ao ser acessado por método GET, redireciona o usuário para a página de login ou para a home do sistema (caso o usuário não esteja logado).
    '''
    return redirect(url_for('login.render_page', next=url_for('home.render_page')))

@login.route('/sistema/login', methods=['GET'])
def render_page():
    '''
    Métodos:
    - GET: renderiza a página Web com o formulário de Login
    - POST: valida os dados fornecidos pelo formulário de Login 
    '''
    form = LoginForm()

    return render_template(
        'login.html', 
        next = url_for('home.render_page'), 
        form = form, 
        messages = get_flashed_messages()
    )

@login.route('/sistema/login/validate', methods=['POST'])
def validate_login():
    form = LoginForm()

    if form.validate_on_submit():
        next = str(form.nextpage.data)
        username = str(form.username.data)
        passwd = str(form.password.data)
        
        try:
            found_user = User.query.filter(User.username == username).first()
            
            if (not (found_user and bcrypt.check_password_hash(found_user.password, passwd) and found_user.status)):
                raise Exception('Usuário ou senha inválidos')
            
            role = UserRole.query.filter_by(id=found_user.role_id).first()
            session['logged_in'] = True
            session['logged_user'] = username
            session['user_role'] = role.desc
            return redirect(url_for('home.render_page'))
        except Exception as e:
            flash(f'Erro ao validar login - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('login.render_page', next=next))
        

@login.route('/sistema/logout', methods=['GET'])
@login_required
def logout():
    '''
    Métodos: 
    - GET: finaliza a sessão do usuário logado no sistema.
    '''
    session.pop('logged_in')
    session.pop('logged_user')
    session.pop('user_role')
    return redirect(url_for('login.render_page', next=url_for('home.render_page')))
