from flask import Blueprint, render_template, jsonify, flash, get_flashed_messages, redirect, url_for, get_flashed_messages, session, request
from app.helpers import login_required
from app.models import Customer, db
from app.clients.forms import *

customers = Blueprint('customers', __name__)

@customers.route('/sistema/home/clientes', methods=['GET'])
@login_required
def render_page():
    customers = NewCustomerForm()
    return render_template('clientes.html', pagetitle='Clientes', new_customer=customers, session=session)

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
    

@customers.route('/api/customers/search', methods=['GET'])
@login_required
def search_customers():
    query = request.args.get('query').lower()

    clients = Customer.query.filter(
        ((Customer.id == query) |
         (Customer.name == query) |
         (Customer.email == query) |
         (Customer.address == query))
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
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('customers.render_page'))

@customers.route('/api/customers/edit', methods=['POST'])
@login_required
def edit_client_data():
    pass

@customers.route('/api/customers/delete', methods=['POST'])
@login_required
def delete_client():
    pass