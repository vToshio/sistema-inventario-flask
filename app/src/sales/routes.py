from flask import Blueprint, current_app, render_template, jsonify, flash, get_flashed_messages, redirect, url_for, session, request
from app.helpers import login_required, flash_messages
from app.models import db, User, Customer, Sale, Product, SaleProducts
from app.src.sales.forms import *

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

@sales.route('/api/sales/register-sale', methods=['POST'])
@login_required
def register_sale():
    form = SaleForm()

    if form.validate_on_submit():
        customer_id = form.customer_id.data
        user_id = form.salesman_id.data
        
        
        try:
            if not Customer.query.filter_by(id=customer_id).first():
                raise Exception('Cliente não encontrado no banco de dados.') 
            
            if not User.query.filter_by(id=user_id).first():
                raise Exception('Vendedor não encontrado no banco de dados.')
            
            sale = Sale(
                total = 0,
                discount = form.discount.data,
                salesman_id = form.salesman_id.data,
                customer_id = form.customer_id.data
            )
            db.session.add(sale)
            db.session.commit()

            total = 0
            for product_form in form.products.entries:
                product = Product.query.filter_by(id=product_form.data['id']).first()

                if not product:
                    raise Exception(f'Produto com ID {product_form.data['id']} não encontrado no banco de dados.')
                
                sale_product = SaleProducts(
                    sale_id = sale.id,
                    product_id = product.id,
                    quantity = product_form.data['quantity']
                ) 
                db.session.add(sale_product)
                total += float(product.price) * float(product_form.data['quantity'])
            
            sale.total = total - (total * (form.discount.data/100))
            db.session.commit()
            flash("Venda registrada com sucesso!")
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar venda - {e}')
    else:
        flash(form.errors)
    return redirect(url_for('sales.render_page'))