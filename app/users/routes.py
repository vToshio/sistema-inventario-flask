from flask import Blueprint, render_template, jsonify, get_flashed_messages, flash, redirect, url_for, request, session
from app.models import db, User, UserRole
from app.users.forms import * 
from app.helpers import login_required, adm_required, flash_messages, bcrypt

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
@adm_required
def render_page():
    new_users = NewUserForm()
    users = User.query.all()
    messages = get_flashed_messages()
    
    return render_template(
        'usuarios.html', 
        pagetitle = 'Usuários',
        new_users=new_users,
        messages = messages,
        session = session,
        users = users
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
            'username' : user.username,
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
    form = NewUserForm()

    if form.validate_on_submit():
        name = str(form.name.data).strip().lower()
        username = str(form.username.data).strip()
        role_id = form.role_id.data
        passwd = str(form.password.data).strip()
        confirm_passwd = str(form.confirm_password.data).strip()
        email = str(form.email.data).strip()

        
        try:
            if User.query.filter_by(email=email).first():
                flash(f'Usuário já cadastrado com o email "{email}".')
            elif User.query.filter_by(username=username).first():
                flash(f'Já existe usuário cadastrado com o username "{username}"')
            elif passwd != confirm_passwd: 
                flash(f'Os campos de senha não são idênticos.')
            else:
                db.session.add(User(
                    name=name, 
                    username=username, 
                    email=email, 
                    role_id=role_id, 
                    password=bcrypt.generate_password_hash(passwd).decode('utf-8'))
                )
                db.session.commit()
                flash(f'Usuário "{username}" criado com sucesso!')
        except Exception as e:
            flash(f'Erro no cadastro de usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))
        

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