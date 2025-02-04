from flask import Blueprint, render_template, jsonify, abort, flash, get_flashed_messages, redirect, url_for, get_flashed_messages, session, request
from app.helpers import login_required, flash_messages, adm_required
from werkzeug.exceptions import HTTPException
from app.models import Customer, db
from app.src.customers.forms import *
from sqlalchemy import text

customers = Blueprint('customers', __name__)

@customers.route('/sistema/home/clientes', methods=['GET'])
@login_required
def render_page():
    '''
    Rota que renderiza a página de clientes.
    '''
    return render_template(
        'clientes.html',
        pagetitle='Clientes', 
        new_customer = NewCustomerForm(), 
        edit_customer = EditCustomerForm(), 
        disable_status = DisableCustomerStatusForm(), 
        reactivate_customer = ReactivateCustomerForm(),
        messages=get_flashed_messages(),
        customers=customers,
        session=session
    )


@customers.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    '''
    Rota da API que retorna uma lista paginada de clientes cadastrados no sistema, através do método GET.

    Query args:
    - page (int): Define a página de clientes em que a tabela se localiza
    - per_page (int): define quantos clientes serão renderizados por página

    Retorno:
    - JSON contendo:
        - 'customers' (list): lista de clientes
            - id: ID de identificação de cliente (int) 
            - name: nome do Cliente (str)
            - status: estado de atividade do cliente (int)
            - cpf: cpf do cliente (str)
            - email: e-mail do cliente (str)
        - 'page' (int): página atual
        - 'on_screen' (int): quantidade de clientes renderizados na página
        - 'per_page' (int): quantidade de clientes por página
        - 'total' (int): quantidade total de clientes
        - 'pages' (int): quantidade total de páginas
    '''
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=1, type=int)

    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    customers_list = [
        {
            'id' : customer.id,
            'name' : str(customer.name).title(),
            'status' : customer.status,
            'cpf' : customer.cpf,
            'email' : str(customer.email),
            'address' : str(customer.address).title(),
        }
        for customer in customers if customer.status and customer.id
    ]
    customers_list.reverse()

    return jsonify(
        {
            'customers' : customers_list,
            'on_screen' : len(customers_list),
            'page' : page,
            'per_page' : per_page,
            'total' : customers.total,
            'pages' : customers.pages
        }
    )
    

@customers.route('/api/customers/<int:id>', methods=['GET'])
@login_required
def get_customer(id: int):
    '''
    Rota dinâmica da API que obtém os dados de um cliente específico, por ID.

    Argumentos:
    - id (int): id que identifica um cliente

    Retorno:
    - JSON contendo:
        - name (str): nome completo do cliente
        - cpf (str): cpf do cliente
        - status (int): status do cliente
        - email (str): email do cliente
        - address (str): endereço do cliente
    '''
    if not isinstance(id, int) or id<0:
        flash('O ID deve ser um número inteiro para realizar uma pesquisa por ID.')
        return redirect(url_for('customers.render_page'))
    
    customer = Customer.query.filter_by(id=id).first()
    if not customer:
       flash('Cliente ainda não cadastrado no banco de dados.')
       return redirect(url_for('customers.render_page'))

    return jsonify(
        {
            'id' : customer.id,
            'name' : str(customer.name).title(),
            'cpf' : customer.cpf,
            'status' : customer.status,
            'email' : customer.email,
            'address' : str(customer.address).title()
        }
    )


@customers.route('/api/customers/search', methods=['GET'])
@login_required
def search_customers():
    '''
    Rota da API que realiza a pesquisa de um cliente por uma query string, utilizando o método GET.

    Query Args:
    - query (str): string que identifica um cliente por id, nome, cpf, email ou endereço.

    Retorno:
    - JSON contendo:
        - 'customers' (list): lista de clientes identificados pela query string.
            - id (int): ID de identificação de cliente (int) 
            - name (str): nome do Cliente (str)
            - status (int): estado de atividade do cliente (int)
            - cpf (str): cpf do cliente (str)
            - email (str): e-mail do cliente (str)
    '''
    searched  = request.args.get('query').strip()

    try:
        query = f'''
            SELECT customer.id as id,
                   customer.name as name,
                   customer.status as status,
                   customer.cpf as cpf,
                   customer.email as email,
                   customer.address as address
            FROM customers customer
            WHERE customer.id LIKE '{searched}' OR
                customer.name LIKE '%{searched}%' OR
                customer.cpf LIKE '{searched}' OR
                customer.email LIKE '{searched}' OR
                customer.address LIKE '%{searched}%'
            ORDER BY customer.id ASC;
        '''
        customers = db.session.execute(text(query)).all()

        customers_list = []
        if customers:
            customers_list.extend([
                {
                    'id' : customer.id,
                    'name' : str(customer.name).title(),
                    'cpf' : customer.cpf,
                    'status' : customer.status,
                    'email' : str(customer.email),
                    'address' : str(customer.address).title()
                }
                for customer in customers
            ])
        return jsonify({'customers' : customers_list})
    except Exception as e:
        print(e)
        flash(f'Erro ao pesquisar cliente - {e}')
        return redirect(url_for('customers.render_page'))


@customers.route('/api/customers/new', methods=['POST'])
@login_required
def new_customer():
    '''
    Rota da API que registra um novo cliente, através do método POST.

    Dados Coletados NewCustomerForm():
    - name (str): nome completo do cliente
    - email (str): email de contato do cliente
    - address (str): endereço do cliente
    '''
    form = NewCustomerForm()

    if form.validate_on_submit():
        name = str(form.name.data).strip().lower()
        cpf = str(form.cpf.data).strip()
        email = str(form.email.data).strip()
        address = str(form.address.data).strip().lower()

        try:
            db.session.add(Customer(name=name, cpf=cpf, email=email, address=address))
            db.session.commit()
            flash(f'Cliente "{name}" cadastrado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro de cliente - {e}')        
    else:
        flash_messages(form.errors)
    return redirect(url_for('customers.render_page'))


@customers.route('/api/customers/edit/<int:id>', methods=['PUT'])
@login_required
def edit_customer(id: int):
    '''
    Rota da API que altera os dados do cliente, através do método POST.

    Dados alterados:
    - name (str): nome completo do cliente
    - email (str): email de contato do cliente
    - address (str): endereço do cliente
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do cliente deve ser do tipo inteiro positivo.'}), 400

    form = EditCustomerForm(data=request.get_json())

    if form.validate():
        id = form.id.data
        try:
            customer = Customer.query.filter_by(id=id).first()
            if not customer:
                raise abort(404, 'Cliente não cadastrado no banco de dados.')
            elif not customer.id:
                raise abort(403, 'Esse cliente não pode ter seus dados alterados.')
            elif not customer.status:
                raise abort(403, 'Não é possível editar os dados de um cliente desativado.')
            
            customer.name = str(form.name.data).strip().lower()
            customer.address = str(form.address.data).strip().lower()
            customer.email = form.email.data
            db.session.commit()
            return jsonify({'message' :f'Edição dos dados do cliente de ID {id} realizada com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' :f'Erro na edição de dados do cliente - {e.description}'}), e.code  
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400


@customers.route('/api/customers/enable-status/<int:id>', methods=['PATCH'])
@adm_required(route='customers.render_page')
@login_required
def reactivate_customer(id: int):
    '''
    Rota da API que reativa um cliente com status inativo, por método PATCH.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do cliente deve ser do tipo inteiro positivo.'}), 400

    form = ReactivateCustomerForm(data=request.get_json())

    if form.validate():
        try:
            id = form.id.data
            customer = Customer.query.filter_by(id=id).first()

            if not customer:
                raise abort(404, f'Usuário com o ID {id} ainda não cadastrado.')
            elif customer.status:
                raise abort(403, f'Usuário com o ID {id} já está ativo.')

            customer.status = 1
            db.session.commit()
            return jsonify({'message' : f'Cliente "{customer.name.title()}" reativado com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' :f'Erro ao reativar cliente - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@customers.route('/api/customers/disable-status/<int:id>', methods=['PATCH'])
@login_required
def disable_customer_status(id:int):
    '''
    Rota da API que desativa um cliente, por método PATCH.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do cliente deve ser do tipo inteiro positivo.'}), 400

    form = DisableCustomerStatusForm(data=request.get_json())

    if form.validate_on_submit():
        try:
            customer = Customer.query.filter_by(id=id).first()

            if not customer:
                abort(404, 'Cliente ainda não registrado.')
            elif not customer.id:
                abort(403, 'Esse cliente não pode ser desativado.')
            if not customer.status:
                abort(403, 'Cliente já está inativo.')
            
            customer.status = 0
            db.session.commit()
            return jsonify({'message' : f'Cliente "{customer.name.title()}" desativado com sucesso!'}), 200    
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao deletar cliente - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem ser preenchidos.'}), 400

