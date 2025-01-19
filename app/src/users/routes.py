from flask import Blueprint, render_template, jsonify, get_flashed_messages, flash, redirect, url_for, request, session
from app.models import db, User, UserRole
from app.src.users.forms import * 
from app.helpers import login_required, adm_required, flash_messages, bcrypt

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
@adm_required()
def render_page():
    new_users = NewUserForm()
    change_passwd = ChangePasswdForm()
    edit_user = EditUserForm()
    delete_user = DeleteUserForm()
    users = User.query.all()
    messages = get_flashed_messages()
    
    return render_template(
        'usuarios.html', 
        pagetitle = 'Usuários',
        new_users = new_users,
        change_passwd = change_passwd,
        edit_user = edit_user,
        delete_user = delete_user,
        messages = messages,
        session = session,
        users = users
    )


@users.route('/api/users/<int:id>', methods=['GET'])
@login_required
@adm_required()
def get_user(id: int):
    user = User.query.filter_by(id=id).first()

    return jsonify({
        'id' : user.id,
        'name' : str(user.name).title(),
        'username' : user.username,
        'role_id' : user.role_id,
        'email' : user.email,
    })


@users.route('/api/users/new', methods=['POST'])
@login_required
@adm_required()
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
        

@users.route('/api/users/mudar-senha', methods=['POST'])
@login_required
@adm_required()
def change_password():
    form = ChangePasswdForm()

    if form.validate_on_submit():
        id = form.id.data
        new_passwd = str(form.new_password.data).strip()
        confirm = str(form.confirm.data).strip()

        if new_passwd != confirm:
            flash('Os campos de senha devem ser idênticos.')
        elif len(new_passwd) < 10:
            flash('A senha deve possuir pelo menos 10 caracteres.')
        else:
            try:
                user = User.query.filter_by(id=id).first()
                if not user:
                    flash(f'Usuário com o id {user.username} não encontrado no banco de dados.')
                else:
                    user.password = bcrypt.generate_password_hash(new_passwd).decode('utf-8')
                    db.session.commit()
                    flash('Senha alterada com sucesso!')
            except Exception as e:
                flash(f'Erro ao realizar mudança de senha - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))

@users.route('/api/users/editar', methods=['POST'])
@login_required
@adm_required()
def edit_user():
    form = EditUserForm()

    if form.validate_on_submit():
        id = form.id.data
        name = str(form.name.data).strip()
        username = str(form.name.data).strip()
        role_id = form.role_id.data
        email = str(form.email.data).strip()

        try:
            user = User.query.filter_by(id=id).first()
            user.name = name
            user.username = username
            user.role_id = role_id
            user.email = email
            db.session.commit()
            flash(f'Usuário {username} alterado com sucesso!')
        except Exception as e:
            flash(f'Erro ao editar usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))

@users.route('/api/users/delete', methods=['POST'])
@login_required
@adm_required()
def delete_user():
    form = DeleteUserForm()

    if form.validate_on_submit():
        id = form.id.data

        try:
            user = User.query.filter_by(id=id).first()
            username = user.username

            if not user:
                flash('Usuário ainda não cadastrado.')
            else:
                db.session.query(User).filter_by(id=id).delete()
                db.session.commit()
                flash(f'Usuário "{username}" removido com sucesso.')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao deletar usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))