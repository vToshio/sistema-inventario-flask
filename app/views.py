from flask import Blueprint, render_template, redirect, url_for, flash, get_flashed_messages, session
from forms import Login

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def root():
    '''
    Define the root endpoint as an unreachable page. 
    It redirects to the home page if the user is logged in or to the login page, if the user isn't.
    '''
    if 'logged_user' in session.keys() and session['logged_user'] is not None:
        return redirect(url_for('views.home'))
    return redirect(url_for('views.login', next=url_for('views.home')))

@views.route('/login', methods=['GET', 'POST'])
def login():
    '''Render the login page.'''
    return render_template('login.html', next=url_for('val.login_validation'), form=Login(), messages=get_flashed_messages(with_categories=True))

@views.route('/logout', methods=['POST'])
def logout():
    '''
    Set the keys 'logged_user' and 'user_role' as None on the current session.
    '''
    session.pop('logged_user', None)
    session.pop('user_role', None)
    return redirect(url_for('views.login', next=url_for('views.home')))

@views.route('/home', methods=['GET', 'POST'])
def home():
    '''
    Render the home webpage if the user is logged in.
    '''
    if'logged_user' not in session.keys() or session['logged_user'] is None:
        flash('Página inacessível enquanto o usuário não estiver logado.', 'error')
        return redirect(url_for('views.login'))
    return render_template('home.html', pagetitle='Home', session=session)

@views.route('/home/vendas')
def vendas():
    return render_template('vendas.html', pagetitle='Vendas', session=session)

@views.route('/home/estoque')
def estoque():
    '''
    Render the stock webpage if the user is logged in.
    '''
    if'logged_user' not in session.keys() or session['logged_user'] is None:
        flash('Página inacessível enquanto o usuário não estiver logado.', 'error')
        return redirect(url_for('views.login'))
    return render_template('estoque.html', pagetitle='Estoque', session=session)

@views.route('/home/compras')
def compras():
    return render_template('compras.html', pagetitle='Compras', session=session)

@views.route('/home/users')
def users_config():
    pass

@views.route('/home/<username>')
def perfil(username: str):
    pass