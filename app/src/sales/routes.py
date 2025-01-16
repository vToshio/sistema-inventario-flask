from flask import Blueprint, render_template, jsonify, flash, get_flashed_messages, redirect, url_for, session, request
from app.helpers import login_required
from app.models import db, User, Customer, Sale, Product, SaleProducts
from app.src.sales.forms import *
from datetime import datetime

sales = Blueprint('sales', __name__)

@sales.route('/sistema/home/vendas', methods=['GET'])
@login_required
def render_page():
    new_sale = SaleForm()
    messages = get_flashed_messages()

    return render_template(
        'vendas.html',
        pagetitle = 'Vendas',
        new_sale = new_sale,
        session = session,
        messages = messages
    )

@sales.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    sales = Sale.query.paginate(page=page, per_page=per_page, error_out=False)

    sale_list = [
        {
            'id' : sale.id,
            'customer' : str(sale.customer.name).title(),
            'salesman' : str(sale.salesman.name).title(),
            'sell_date' : sale.sell_date.strftime('%d/%m/%Y'),
            'total' : sale.total
        }
        for sale in sales.items
    ]

    return jsonify(
        {
            'sales' : sale_list,
            'page' : sales.page,
            'per_page' : per_page,
            'total' : sales.total,
            'pages' : sales.pages
        }
    )

@sales.route('/api/sales/search', methods=['GET'])
@login_required
def search_sale():
    query = str(request.args.get('query')).strip()

    sales = Sale.query.join(User).join(Customer).filter(
        ((Sale.id == query) |
         (Customer.name == query.lower()) |
         (User.name == query.lower()))
    ).all()

    sales_list = [
        {
            'id' : sale.id,
            'customer' : str(sale.customer.name).title(),
            'salesman' : str(sale.salesman.name).title(),
            'sell_date' : sale.sell_date.strftime('%d/%m/%Y'),
            'total' : sale.total
        }
        for sale in sales
    ]

    return jsonify({'sales' : sales_list})

@sales.route('/api/sales/register-sale', methods=['POST'])
@login_required
def register_sale():
    form = SaleForm()

    if form.validate_on_submit():
        customer_id = form.customer_id.data
        user_id = form.salesman_id.data
        discount = form.discount.data
        
        try:
            if not Customer.query.filter_by(id=customer_id).first():
                raise Exception('Cliente não encontrado no banco de dados.') 
            
            if not User.query.filter_by(id=user_id).first():
                raise Exception('Vendedor não encontrado no banco de dados.')
            
            sale = Sale(
                total = 0,
                discount = discount,
                salesman_id = user_id,
                customer_id = customer_id
            )
            db.session.add(sale)

            total = 0
            for product_form in form.products.entries:
                product = Product.query.filter_by(id=product_form.data['id']).first()

                if not product:
                    raise Exception(f'Produto com ID {product_form.data['id']} não encontrado no banco de dados.')
                elif product.quantity == 0:
                    raise Exception(f'Não há produtos de ID {product.id} em estoque.')
                elif product.quantity < product_form.data['quantity']:
                    raise Exception(f'Existem apenas {product.quantity} unidades do produto de ID {product.id} em estoque.')

                sale_product = SaleProducts(
                    sale_id = sale.id,
                    product_id = product.id,
                    quantity = product_form.data['quantity']
                ) 
                total += float(product.price) * float(product_form.data['quantity'])
                product.quantity -= product_form.data['quantity']
                db.session.add(sale_product)
            
            sale.total = total - (total * (discount/100))
            
            db.session.commit()
            flash("Venda registrada com sucesso!")
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar venda - {e}')
    else:
        flash(form.errors)
    return redirect(url_for('sales.render_page'))