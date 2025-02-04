from flask import Blueprint, render_template, abort, jsonify, get_flashed_messages, flash, redirect, url_for, request, session
from app.helpers import login_required, adm_required, flash_messages, bcrypt
from app.models import db, User
from app.src.users.forms import * 
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

users = Blueprint('users', __name__)

@users.route('/sistema/home/usuarios', methods=['GET'])
@login_required
@adm_required()
def render_page():
    '''
    Rota que renderiza a página de Usuários por método GET.
    '''
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
    '''
    Rota da API que retorna uma lista de usuários.

    Query Args:
    - page: página atual da lista
    - per_page: quantas vendas estarão disponíveis por exibição de página

    Retorno: 
    - 'users' (List): lista de dicionários contendo os dados dos usuários
        'id' (int): ID do usuário
        'name' (str): nome do usuário 
        'username' (str): nome de acesso do sistema
        'status' (int): estado de atividade do usuário 
        'role_id' (int): ID do cargo do usuário
        'role' (str): descrição do cargo do usuário
        'email' (str): e-mail do usuário 
        'date_created' (date): data de criação do usuário
    - 'on_screen' (int): quantidade de usuários renderizados na página
    - 'per_page' (int): quantas usuários serão renderizados por página
    - 'total' (int): total de usuários
    - 'pages' (int): total de páginas
    '''
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
    users_list.reverse()

    return jsonify({
        'users' : users_list,
        'on_screen' : len(users_list),
        'per_page' : users.per_page,
        'page' : users.page,
        'total' : users.total,
        'pages' : users.pages
    })


@users.route('/api/users/search', methods=['GET'])
@login_required
@adm_required()
def search_users():
    '''
    Rota da API que realiza a pesquisa de um usuário com base no seu ID, nome, nome de usuário, cargo ou e-mail.

    Query Args:
    - query (str): valor a ser pesquisado no banco de dados.

    Retorno: 
    - 'users': lista de dicionários contendo os dados dos usuários
        'id' (int): ID do usuário
        'name' (str): nome do usuário 
        'username' (str): nome de acesso do sistema
        'status' (int): estado de atividade do usuário 
        'role_id' (int): ID do cargo do usuário
        'role' (str): descrição do cargo do usuário
        'email' (str): e-mail do usuário 
        'date_created' (date): data de criação do usuário
    '''
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
    '''
    Rota dinâmica da API que pega os dados básicos de um único usuário.

    Retorno (JSON):
    - id (int): ID do usuário
    - name (str): nome completo do usuário
    - username (str): nome de acesso do sistema
    - role_id (int): ID do cargo do usuário
    - email (str): e-mail do usuário
    '''

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
    '''
    Rota da API que registra um novo usuário por método POST.

    Dados Registrados:
    - name (str): nome completo do usuário
    - username (str): nome de acesso do sistema
    - role_id (int): ID do cargo do usuário
    - passwd (str): senha do usuário, encriptada pelo Flask Bcrypt
    - email (str): email do usuário
    '''
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
        

@users.route('/api/users/change-password/<int:id>', methods=['PATCH'])
@login_required
@adm_required()
def change_password(id: int):
    '''Rota da API que modifica a senha atual do usuário por método PATCH.'''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do usuário deve ser do tipo inteiro.'}), 400

    form = ChangePasswdForm(data=request.get_json())    

    if form.validate():
        new_passwd = str(form.new_password.data).strip()
        confirm = str(form.confirm.data).strip()

        try:
            if not id:
                abort(403, 'Não é possível trocar a senha deste usuário.')
            if new_passwd != confirm:
                abort(400, 'Os campos de senha devem ser idênticos.')
            elif len(new_passwd) < 10:
                abort(400, 'A senha deve possuir pelo menos 10 caracteres.')
        
            user = User.query.filter_by(id=id).first()

            if not user:
                abort(404, f'Usuário com o ID {id} não encontrado no banco de dados.')
            elif not user.status:
                abort(403, f'Não é possível mudar a senha do usuário "{user.username}" pois ele está desativado.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                abort(403, 'Um usuário administrador não pode mudar a senha de outro usuário administrador.')
            
            user.password = bcrypt.generate_password_hash(new_passwd).decode('utf-8')
            db.session.commit()
            return jsonify({'message' : 'Senha alterada com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao realizar mudança de senha - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos precisam estar preenchidos.'}), 400

@users.route('/api/users/edit/<int:id>', methods=['PUT'])
@login_required
@adm_required()
def edit_user(id: id):
    '''
    Rota que edita os dados de um usuário por método PUT.

    Dados Editados:
    - name (str): nome completo do usuário
    - username (str): nome de acesso do sistema
    - email (str): email do usuário
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message': 'o ID do usuário deve ser do tipo inteiro.'}), 400
    
    form = EditUserForm(data=request.get_json())

    if form.validate():
        try:
            if not id:
                abort(403, 'Os dados desse usuário não podem ser editados.')
            
            user = User.query.filter_by(id=id).first()
            old_username = user.username

            if not user:
                abort(404, 'Usuário não encontrado no banco de dados.')
            elif not user.status:
                abort(403, f'Não é possível editar os dados do usuário "{user.username}" pois ele está desativado.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                abort(403, 'Um usuário administrador não pode editar os dados de outro administrador.')

            if session['logged_user'] == user.username:
                session['logged_user'] = form.username.data.strip()
            
            user.name = str(form.name.data).lower().strip()
            user.username = str(form.username.data).strip()
            user.email = str(form.email.data).strip()
            db.session.commit()
            return jsonify({'message' : f'Usuário {old_username} alterado com sucesso! Atualizando os dados na tela...'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao editar usuário - {e.description}'}), e.code 
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@users.route('/api/users/edit-role/<int:id>', methods=['PATCH'])
@login_required
@adm_required()
def edit_role(id: int):
    '''
    Rota da API que realiza a edição de um cargo de um usuário no sistema, por método PATCH.
    Somente o usuário Master consegue realizar essa ação.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do usuário deve ser um valor inteiro.'}), 400

    form = EditRoleForm(data=request.get_json())

    if form.validate():
        role_id = form.role_id.data

        try:
            if not id:
                abort(403, 'Esse usuário não pode ter o cargo alterado.')
            elif session['user_role'] != 'master':
                abort(403, 'Somente o usuário Master pode realizar a alteração de cargos de usuários')
            
            user = User.query.filter_by(id=id).first()
            
            if not user:
                abort(404, 'Usuário não encontrado no banco de dados.')
            elif not int(role_id) in [role.id for role in UserRole.query.all()]:
                abort('Atribuição de cargo inexistente.')

            user.role_id = role_id
            db.session.commit()
            return jsonify({'message' : f'Alteração de cargo do usuário "{user.username}" realizada com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao realizar edição de cargos - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@users.route('/api/users/enable-status/<int:id>', methods=['PATCH'])
@login_required
@adm_required()
def enable_status(id:int):
    '''
    Rota da API que reabilita o estado de um usuário para ativo no sistema, utilizando o método PATCH
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do usuário deve ser um valor inteiro.'}), 400
    
    form = EnableStatusForm(data=request.get_json())

    if form.validate():
        try:
            user = User.query.filter_by(id=id).first()

            if not user:
                abort(404, f'Usuário não encontrado no banco de dados.')
            elif user.status:
                abort(403, f'O usuário {user.username} já está ativo.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                abort(403, 'Um usuário administrador não pode ativar outro usuário administrador.')

            user.status = 1
            db.session.commit()
            return jsonify({'message' : f'Usuário {user.username} reativado com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' :f'Erro ao reativar usuário - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@users.route('/api/users/disable-status/<int:id>', methods=['PATCH'])
@login_required
@adm_required()
def disable_status(id:int):
    '''
    Rota da API que torna um usuário inativo no sistema por meio do método POST.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do usuário deve ser um valor inteiro.'}), 400
    
    form = DisableStatusForm(data=request.get_json())

    if form.validate_on_submit():
        try:
            if not id:
                abort(403, f'Esse usuário não pode ser desativado.')

            user = User.query.filter_by(id=id).first()

            if not user:
                abort(404, 'Usuário não encontrado no banco de dados.')
            elif not user.status:
                abort(403, f'Usuário "{user.username}" já está desativado.')
            elif user.username == session['logged_user']:
                abort(403, 'Um usuário não pode desativar sua própria conta.')
            elif (user.roles.desc == 'admin' and (session['user_role'] == 'admin' and session['logged_user'] != user.username)):
                abort(403, 'Um usuário administrador não pode desativar outro usuário administrador.')

            user.status = 0
            db.session.commit()
            return jsonify({'message' : f'Usuário "{user.username}" foi desativado com sucesso.'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao deletar usuário - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400