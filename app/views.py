from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages, session, request
from flask_bcrypt import Bcrypt
from helpers import login_required
from forms import *
from models import *

views = Blueprint('views', __name__)
bcrypt = Bcrypt()

@views.route('/', methods=['GET'])
@login_required
def root():
    '''
    Endpoint root, que ao ser acessado por método GET, redireciona o usuário para a página de login ou para a home do sistema (caso o usuário não esteja logado).
    '''
    return redirect(url_for('views.login', next=url_for('views.home')))

@views.route('/sistema/error/<error_name>')
def error(error: str):
    return render_template('erro.html', pagetitle='Erro de acesso' ,error=error)

@views.route('/sistema/login', methods=['GET', 'POST'])
def login():
    '''
    Métodos:
    - GET: renderiza a página Web com o formulário de Login
    - POST: valida os dados fornecidos pelo formulário de Login 
    '''
    try:
        # If POST HTTP
        if request.method == 'POST':
            form = LoginForm()

            if form.validate_on_submit():
                next = form.nextpage.data
                username = form.username.data
                passwd = form.password.data
        
            found_user = User.query.filter(User.username == username).first()
            if found_user:
                if bcrypt.check_password_hash(found_user.password, passwd):
                    session['logged_user'] = username
                    session['user_role'] = found_user.role
                    return redirect(url_for('views.home'))
                flash('Senha incorreta.', 'error')
            else:
                flash('Usuário ainda não cadastrado.', 'error')
            return redirect(url_for('views.login', next=next))
        
        # If GET HTTP
        form = LoginForm()
        return render_template('login.html', next=url_for('views.login'), form=form, messages=get_flashed_messages(with_categories=True))
    except Exception as e:
        return redirect(url_for('views.error', error=e))

@views.route('/sistema/logout', methods=['POST'])
def logout():
    '''
    Métodos: 
    - POST: finaliza a sessão do usuário logado no sistema.
    '''
    try:
        session.pop('logged_user')
        session.pop('user_role')
        return redirect(url_for('views.login', next=url_for('views.home')))
    except Exception as e:
        return redirect(url_for('views.error', error=e))

@views.route('/sistema/home', methods=['GET'])
@login_required
def home():
    '''
    Métodos:
    - GET: renderiza a página Home do sistema.
    '''
    return render_template('home.html', pagetitle='Home', session=session)

@views.route('/sistema/home/estoque', methods=['GET'])
@login_required
def inventory():
    '''
    Métodos:
    - GET: Renderiza a página de gerenciamento do estoque.
    '''
    try:
        products = Product.query.first()
        categories = ProductCategory.query.all()
        new_product = NewProductForm()
        messages = get_flashed_messages()

        return render_template('estoque.html', pagetitle='Estoque', new_product=new_product, messages=messages, categories=categories, products=products, session=session)
    except Exception as e:
        flash(f'Falha ao carregar arquivos do estoque: {e}')
        return redirect(url_for('views.home'))

@views.route('/sistema/home/vendas')
@login_required
def sales():
    return render_template('vendas.html', pagetitle='Vendas', session=session)

@views.route('/sistema/home/clientes')
@login_required
def clients():
    return render_template('clientes.html', pagetitle='Clientes', session=session)

@views.route('/sistema/home/users')
@login_required
def users_config():
    pass

@views.route('/sistema/home/profile/<username>')
@login_required
def profile(username: str):
    pass