from flask import Blueprint, render_template, jsonify, flash, get_flashed_messages, redirect, url_for, get_flashed_messages, session, request
from app.helpers import login_required, flash_messages
from app.models import Customer, db
from app.src.clients.forms import *

customers = Blueprint('customers', __name__)

@customers.route('/sistema/home/clientes', methods=['GET'])
@login_required
def render_page():
    '''
    Rota que renderiza a página de clientes.
    '''
    customers = Customer.query.first()

    return render_template(
        'clientes.html',
        pagetitle='Clientes', 
        new_customer = NewCustomerForm(), 
        edit_customer = EditCustomerForm(), 
        delete_customer = DeleteCustomerForm(), 
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
        - 'page' (int): página atual
        - 'per_page' (int): quantidade de clientes por página
        - 'total' (int): quantidade total de clientes
        - 'pages' (int): quantidade total de páginas
    '''
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=1, type=int)

    clients = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    clients_list = [
        {
            'id' : client.id,
            'name' : str(client.name).title(),
            'email' : str(client.email),
            'address' : str(client.address).title(),
        }
        for client in clients
    ]

    return jsonify(
        {
            'customers' : clients_list,
            'page' : page,
            'per_page' : per_page,
            'total' : clients.total,
            'pages' : clients.pages
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
        - 'name' (str): nome completo do cliente,
        - ''
    '''
    if not isinstance(id, int):
        flash('O ID deve ser um número inteiro para realizar uma pesquisa por ID.')
        return redirect(url_for('customers.render_page'))
    
    customer = Customer.query.filter_by(id=id).first()
    if not customer:
       flash('Cliente ainda não cadastrado no banco de dados.')
       return redirect(url_for('customers.render_page'))

    return jsonify(
        {
            'name' : str(customer.name).title(),
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
    - query (str): string que identifica um cliente por id, nome, email ou endereço.

    Retorno:
    - JSON contendo:
        - 'customers' (list): lista de clientes identificados pela query string.
    '''
    query = request.args.get('query').strip()

    clients = Customer.query.filter(
        ((Customer.id == query) |
         (Customer.name == query.lower()) |
         (Customer.email == query) |
         (Customer.address == query.lower()))
    ).all()

    customers_list = [
        {
            'id' : customer.id,
            'name' : str(customer.name).title(),
            'email' : str(customer.email),
            'address' : str(customer.address).title()
        }
        for customer in clients
    ]

    return jsonify({'customers' : customers_list})


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
        email = str(form.email.data).strip()
        address = str(form.address.data).strip().lower()

        try:
            db.session.add(Customer(name=name, email=email, address=address))
            db.session.commit()
            flash(f'Cliente "{name}" cadastrado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro de cliente - {e}')        
    else:
        flash_messages(form.errors)
    return redirect(url_for('customers.render_page'))


@customers.route('/api/customers/edit', methods=['POST'])
@login_required
def edit_customer():
    '''
    Rota da API que altera os dados do cliente, através do método POST.

    Dados alterados:
    - name (str): nome completo do cliente
    - email (str): email de contato do cliente
    - address (str): endereço do cliente
    '''
    form = EditCustomerForm()

    if form.validate_on_submit():
        id = form.id.data
        try:
            customer = Customer.query.filter_by(id=id).first()
            if not customer:
                raise Exception('Cliente não cadastrado no banco de dados.')
            customer.name = str(form.name.data).strip().lower()
            customer.address = str(form.address.data).strip().lower()
            customer.email = form.email.data
            db.session.commit()
            flash(f'Edição dos dados do cliente de ID {id} realizada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro na edição de dados do cliente - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('customers.render_page'))


@customers.route('/api/customers/delete', methods=['POST'])
@login_required
def delete_customer():
    '''
    Rota da API que deleta um cliente do banco de dados, por método POST.
    '''
    form = DeleteCustomerForm()

    if form.validate_on_submit():
        id = form.id.data

        try:
            customer = Customer.query.filter_by(id=id).first()

            if not customer:
                raise Exception('Cliente ainda não registrado.')
            elif customer.id == 1:
                raise Exception('Não é possível deletar esse cliente.')

            name = str(customer.name).title()
            db.session.query(Customer).filter_by(id=id).delete()
            db.session.commit()
            flash(f'Cliente "{name}" deletado com sucesso!')    
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao deletar cliente - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('customers.render_page'))