from flask import Blueprint, render_template, jsonify, get_flashed_messages, flash, redirect, url_for, request, session
from app.models import db, User, UserRole
from app.users.forms import * 
from app.helpers import login_required, adm_required

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
@adm_required
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
@adm_required
def get_users():
    users = User.query.all()

    users_list = [
        {
            'id' : user.id,
            'name' : str(user.name).title(),
            'username' : user.name,
            'role' : str(user.roles.desc).title(),
            'email' : user.email,
            'date_created' : user.date_created
        }
        for user in users
    ]
    
    return jsonify({
        'users' : users_list,
        'total' : len(users_list)
    })

@users.route('/api/users/search', methods=['GET'])
@login_required
@adm_required
def search_users():
    query = request.args.get('query')

    users = User.query.join(UserRole).filter(
        ((User.id == query) |
         (User.name == str(query).lower()) |
         (User.username == query) | 
         (UserRole.desc == str(query).lower()) |
         (User.email == query))
    ).all()
    
    users_list = [
        {
            'id' : user.id,
            'name' : str(user.name).title(),
            'username' : user.name,
            'role' : str(user.roles.desc).title(),
            'email' : user.email,
            'date_created' : user.date_created
        }
        for user in users
    ]

    return jsonify({'users' : users_list})

@users.route('/api/users/new', methods=['POST'])
@login_required
@adm_required
def new_user():
    pass

@users.route('/api/users/edit', methods=['POST'])
@login_required
@adm_required
def edit_user():
    pass

@users.route('/api/users/delete', methods=['POST'])
@login_required
@adm_required
def delete_user():
    pass 