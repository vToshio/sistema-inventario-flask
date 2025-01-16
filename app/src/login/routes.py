from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages, session, request
from app.helpers import login_required, bcrypt
from app.src.login.forms import LoginForm
from app.models import *

login = Blueprint('login', __name__)

@login.route('/', methods=['GET'])
@login_required
def root():
    '''
    Endpoint root, que ao ser acessado por método GET, redireciona o usuário para a página de login ou para a home do sistema (caso o usuário não esteja logado).
    '''
    return redirect(url_for('login.render_page', next=url_for('home.render_page')))

@login.route('/sistema/error/<error_name>')
def error(error: str):
    return render_template('erro.html', pagetitle='Erro de acesso' ,error=error)

@login.route('/sistema/login', methods=['GET', 'POST'])
def render_page():
    '''
    Métodos:
    - GET: renderiza a página Web com o formulário de Login
    - POST: valida os dados fornecidos pelo formulário de Login 
    '''
    try:
        # POST
        if request.method == 'POST':
            form = LoginForm()

            if form.validate_on_submit():
                next = str(form.nextpage.data)
                username = str(form.username.data)
                passwd = str(form.password.data)
        
                found_user = User.query.filter(User.username == username).first()
                if found_user and bcrypt.check_password_hash(found_user.password, passwd):
                    role = UserRole.query.filter_by(id=found_user.role_id).first()
                    session['logged_user'] = username
                    session['user_role'] = role.desc
                    return redirect(url_for('home.render_page'))
            else:
                flash('Usuário ou senha inválidos.')
            return redirect(url_for('login.render_page', next=next))
        
        # GET
        form = LoginForm()
        return render_template('login.html', next=url_for('login.render_page'), form=form, messages=get_flashed_messages(with_categories=True))
    except Exception as e:
        flash(f'Erro ao validar usuário - {e}')
        return redirect(url_for('views.login'))

@login.route('/sistema/logout', methods=['GET'])
@login_required
def logout():
    '''
    Métodos: 
    - GET: finaliza a sessão do usuário logado no sistema.
    '''
    session.pop('logged_user')
    session.pop('user_role')
    return redirect(url_for('login.render_page', next=url_for('home.render_page')))
