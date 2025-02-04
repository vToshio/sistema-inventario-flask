from flask import Blueprint, render_template, session
from app.helpers import login_required
from app.models import User, Customer, Product, SaleProducts, Sale, db
from sqlalchemy import text, func
from math import floor

home = Blueprint('home', __name__)

@home.route('/sistema/home', methods=['GET'])
@login_required
def render_page():
    '''
    Métodos:
    - GET: renderiza a página Home do sistema.

    Principais Argumentos Renderizados:
    - qt_sales (int): valor que define a quantidade de vendas registradas.
    - qt_customers (int): valor que define a quantidade de clientes registrados, não incluindo o 'Não Registrado'.
    - qt_users (int): valor que define a quantidade de colaboradores que utilizam o sistema, não incluindo o Usuário 'Master'.
    - qt_products (int): valor que define a quantidade de produtos em estoque.
    - qt_sale_products (int): valor que define a quantidade de produtos vendidos.
    - total (int): valor que define o valor total de dinheiro arrecadados por venda.
    '''
    user = User.query.filter_by(username=session['logged_user']).first()
    first_name = ''
    for ch in user.name:
        if ch == ' ':
            break
        first_name += ch

    total = db.session.execute(text('SELECT SUM(sales.total) FROM sales;')).first()
    products = db.session.execute(text('SELECT SUM(products.quantity) FROM products WHERE    products.status = 1;')).first()
    sale_products = db.session.execute(text('SELECT SUM(products.quantity) FROM sale_products products;')).first()
    customers = Customer.query.filter((Customer.status == 1) & (Customer.id > 0)).count()
    users = User.query.filter_by(status=1).count()
    sales = Sale.query.count()

    return render_template(
        'home.html',
        pagetitle='Home',
        name = first_name.title(),
        role = str(user.roles.desc).title(),  
        session = session,
        qt_sales = sales,
        qt_customers = customers,
        qt_users = users-1 if users else 0,
        qt_products = products[0] if products is not None else 0,
        qt_sale_products = sale_products[0] if sale_products[0] is not None else 0  ,
        total = floor(total[0]) if total[0] is not None else 0
    )