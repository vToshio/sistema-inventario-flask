from flask import Blueprint, render_template, get_flashed_messages, flash, redirect, url_for, request, session
from app.users.forms import * 
from app.helpers import login_required

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
def render_page():
    messages = get_flashed_messages()
    
    return render_template(
        'usuarios.html', 
        pagetitle = 'Usuários',
        messages = messages,
        session = session
    )


@users.route('/api/users/get', methods=['GET'])
@login_required
def get_users():
    pass

@users.route('/api/users/search', methods=['GET'])
@login_required
def search_users():
    pass

@users.route('/api/users/new', methods=['POST'])
@login_required
def new_user():
    pass

@users.route('/api/users/edit', methods=['POST'])
@login_required
def edit_user():
    pass

@users.route('/api/users/delete', methods=['POST'])
@login_required
def delete_user():
    pass