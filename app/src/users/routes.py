from flask import Blueprint, render_template, jsonify, get_flashed_messages, flash, redirect, url_for, request, session
from app.helpers import login_required, adm_required, flash_messages, bcrypt
from app.models import db, User
from app.src.users.forms import * 
from sqlalchemy import text

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
@adm_required()
def render_page():
    users = [user for user in User.query.all() if user.id and user.status]

    return render_template(
        'usuarios.html', 
        pagetitle = 'Usuários',
        new_users = NewUserForm(),
        change_passwd = ChangePasswdForm(),
        edit_user = EditUserForm(),
        edit_role = EditRoleForm(),
        disable_status = DisableStatusForm(),
        enable_status = EnableStatusForm(),
        messages = get_flashed_messages(),
        session = session,
        users = users
    )


@users.route('/api/users', methods=['GET'])
@login_required
@adm_required()
def get_users():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    users_list = [
        {
            'id' : user.id,
            'name' : str(user.name).title(),
            'username' : user.username,
            'status' : user.status,
            'role_id' : user.role_id,
            'role' : str(user.roles.desc).title(),
            'email' : user.email,
            'date_created' : user.date_created.strftime('%d/%m/%Y')
        }
        for user in users if user.status and user.id
    ]

    return jsonify({
        'users' : users_list,
        'per_page' : users.per_page,
        'page' : users.page,
        'total' : users.total
    })


@users.route('/api/users/search', methods=['GET'])
@login_required
@adm_required()
def search_users():
    searched = request.args.get('query', default='').strip().lower()

    try:
        query = f'''
            SELECT users.id AS id,
                   users.name AS name,
                   users.username AS username,
                   users.status AS status,
                   users.role_id as role_id,
                   roles.desc AS role,
                   users.email AS email,
                   STRFTIME('%d/%m/%Y', users.date_created) AS date_created
            FROM users
                INNER JOIN roles ON users.role_id = roles.id
            WHERE users.id LIKE '{searched}' OR
                  users.name LIKE '%{searched}%' OR
                  LOWER(users.username) LIKE '%{searched}%' OR
                  roles.desc LIKE '%{searched}%' OR
                  LOWER(users.email) LIKE '%{searched}%'
            ORDER BY users.id ASC;
        '''
        users = db.session.execute(text(query)).all()

        users_list = []
        if users: 
            users_list.extend([
                {
                    'id' : user.id,
                    'name' : str(user.name).title(),
                    'username' : user.username,
                    'status' : user.status,
                    'role_id' : user.role_id,
                    'role' : str(user.role).title(),
                    'email' : user.email,
                    'date_created' : user.date_created
                }
                for user in users
            ])

        return jsonify({'users' : users_list})
    except Exception as e:
        print(e)
        flash(f'Erro ao realizar pesquisa de usuários - {e}')
        return redirect(url_for('users.render_page'))

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
            if not role_id:
                raise Exception('Não é possível criar um usuário com esse cargo.')

            user_email = User.query.filter_by(email=email).first()
            user_username = User.query.filter_by(username=username).first()

            if user_email:
                raise Exception(f'Usuário já cadastrado com o email "{email}".')
            elif user_username:
                raise Exception(f'Já existe usuário cadastrado com o username "{username}"')
            elif passwd != confirm_passwd: 
                raise Exception(f'Os campos de senha não são idênticos.')
           
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
            db.session.commit()
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

        try:
            if not id:
                raise Exception('Não é possível trocar a senha deste usuário.')
            if new_passwd != confirm:
                raise Exception('Os campos de senha devem ser idênticos.')
            elif len(new_passwd) < 10:
                raise Exception('A senha deve possuir pelo menos 10 caracteres.')
        
            user = User.query.filter_by(id=id).first()

            if not user:
                raise Exception(f'Usuário com o ID {id} não encontrado no banco de dados.')
            elif not user.status:
                raise Exception(f'Não é possível mudar a senha do usuário "{user.username}" pois ele está desativado.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                raise Exception('Um usuário administrador não pode mudar a senha de outro usuário administrador.')
            
            user.password = bcrypt.generate_password_hash(new_passwd).decode('utf-8')
            db.session.commit()
            flash('Senha alterada com sucesso!')
        except Exception as e:
            db.session.rollback()
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
        username = str(form.username.data).strip()
        email = str(form.email.data).strip()

        try:
            if not id:
                raise Exception('Os dados desse usuário não podem ser editados.')
            
            user = User.query.filter_by(id=id).first()

            if not user:
                raise Exception('Usuário não encontrado no banco de dados.')
            elif not user.status:
                raise Exception(f'Não é possível editar os dados do usuário "{user.username}" pois ele está desativado.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                raise Exception('Um usuário administrador não pode editar os dados de outro administrador.')

            if session['logged_user'] == user.username:
                session['logged_user'] = username
            
            user.name = name
            user.username = username
            user.email = email
            db.session.commit()
            flash(f'Usuário {username} alterado com sucesso!')
        except Exception as e:
            flash(f'Erro ao editar usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))

@users.route('/api/users/edit-role', methods=['POST'])
@login_required
@adm_required()
def edit_role():
    form = EditRoleForm()

    if form.validate_on_submit():
        id = form.id.data
        role_id = form.role_id.data

        try:
            if id == 1:
                raise Exception('Esse usuário não pode ter o cargo alterado.')
            elif session['user_role'] != 'master':
                raise Exception('Somente o usuário Master pode realizar a alteração de cargos de usuários')
            
            user = User.query.filter_by(id=id).first()
            
            if not user:
                raise Exception('Usuário não encontrado no banco de dados.')
            elif not int(role_id) in [role.id for role in UserRole.query.all()]:
                raise Exception('Atribuição de cargo inexistente.')

            user.role_id = role_id
            db.session.commit()
            flash(f'Alteração de cargo do usuário "{user.username}" realizada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao realizar edição de cargos - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))

@users.route('/api/users/enable-status', methods=['POST'])
@login_required
@adm_required()
def enable_status():
    form = EnableStatusForm()

    if form.validate_on_submit():
        id = form.id.data

        try:
            user = User.query.filter_by(id=id).first()

            if not user:
                raise Exception(f'Usuário não encontrado no banco de dados.')
            elif user.status:
                raise Exception(f'O usuário {user.username} já está ativo.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                raise Exception('Um usuário administrador não pode ativar outro usuário administrador.')

            user.status = 1
            db.session.commit()
            flash(f'Usuário {user.username} reativado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao reativar usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))

@users.route('/api/users/disable-status', methods=['POST'])
@login_required
@adm_required()
def disable_status():
    form = DisableStatusForm()

    if form.validate_on_submit():
        id = form.id.data
        try:
            if not id:
                raise Exception(f'Esse usuário não pode ser desativado.')

            user = User.query.filter_by(id=id).first()

            if not user:
                raise Exception('Usuário não encontrado no banco de dados.')
            elif not user.status:
                raise Exception(f'Usuário "{user.username}" já está desativado.')
            elif user.username == session['logged_user']:
                raise Exception('Um usuário não pode desativar sua própria conta.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                raise Exception('Um usuário administrador não pode desativar outro usuário administrador.')

            user.status = 0
            db.session.commit()
            flash(f'Usuário "{user.username}" foi desativado com sucesso.')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao deletar usuário - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('users.render_page'))