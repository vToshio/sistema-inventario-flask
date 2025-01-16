from flask import Blueprint, render_template, session
from app.helpers import login_required

home = Blueprint('home', __name__)

@home.route('/sistema/home', methods=['GET'])
@login_required
def render_page():
    '''
    Métodos:
    - GET: renderiza a página Home do sistema.
    '''
    return render_template('home.html', pagetitle='Home', session=session)