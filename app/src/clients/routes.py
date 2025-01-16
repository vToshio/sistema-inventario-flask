from flask import Blueprint, render_template, jsonify, flash, get_flashed_messages, redirect, url_for, get_flashed_messages, session, request
from app.helpers import login_required, flash_messages
from app.models import Customer, db
from app.src.clients.forms import *

customers = Blueprint('customers', __name__)

@customers.route('/sistema/home/clientes', methods=['GET'])
@login_required
def render_page():
    customers = Customer.query.first()

    new_customer = NewCustomerForm()
    delete_customer = DeleteCustomerForm()
    edit_customer = EditCustomerForm()
    return render_template(
        'clientes.html',
        pagetitle='Clientes', 
        new_customer=new_customer, 
        edit_customer=edit_customer, 
        delete_customer=delete_customer, 
        messages=get_flashed_messages(),
        customers=customers,
        session=session
    )


@customers.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
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
    query = request.args.get('query').strip()

    clients = Customer.query.filter(
        ((Customer.id == query) |
         (Customer.name == query.lower()) |
         (Customer.email == query) |
         (Customer.address == query.lower()))
    ).all()

    print(clients)

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
    form = EditCustomerForm()

    if form.validate_on_submit():
        id = form.id.data
        customer = Customer.query.filter_by(id=id).first()
        if not customer:
            flash('Cliente não cadastrado no banco de dados.')
        else:
            try:
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
    form = DeleteCustomerForm()

    if form.validate_on_submit():
        id = form.id.data

        customer = Customer.query.filter_by(id=id).first()

        if not customer:
            flash('Cliente ainda não registrado.')
        else:
            try:
                name = str(customer.name).title()
                db.session.query(Customer).filter_by(id=id).delete()
                db.session.commit()
                flash(f'Cliente "{name}" deletado com sucesso!')    
            except Exception as e:
                db.session.rollback()
                flash(f'Cliente não encontrado no banco de dados - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('customers.render_page'))