from flask import Blueprint, render_template,make_response, jsonify, flash, get_flashed_messages, redirect, url_for, session, request
from app.helpers import login_required
from app.models import db, User, Customer, Sale, Product, SaleProducts
from app.src.sales.forms import *
from sqlalchemy import text
import pdfkit

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


@sales.route('/sistema/home/vendas/<int:sale_id>', methods=['GET'])
@login_required
def download_pdf(sale_id: int):
    try:
        sale = Sale.query.filter_by(id=sale_id).first()
        salesman = User.query.join(Sale).filter(Sale.id==sale_id).first()
        customer = Customer.query.join(Sale).filter(Sale.id==sale_id).first()

        products = []
        subtotal = 0
        total = 0
        for sale_product in SaleProducts.query.filter_by(sale_id=sale_id).all():
            prod = {
                'product_data' : Product.query.filter_by(id=sale_product.product_id).first(),
                'sale_quantity' : sale_product.quantity
            }
            subtotal += prod['product_data'].price * prod['sale_quantity']
            products.append(prod)
        
        total = subtotal - (subtotal * sale.discount/100)
        discount = subtotal - total
        rendered = render_template(
            'nota_fiscal.html',
            pagetitle = 'Nota Fiscal',
            sale = sale,
            products = products,
            customer = customer,
            salesman = salesman,
            subtotal = round(subtotal, 2),
            total = round(total, 2),
            discount = round(discount, 2)
        )

        pdf = pdfkit.from_string(rendered, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pd'
        response.headers['Content-Disposition'] = f'inline;filename="nf-{sale_id}-{sale.sell_date}.pdf"'

        return response
    except Exception as e:
        flash(f'Erro ao baixar pdf - {e}')
        return redirect(url_for('sales.render_page'))


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
    searched = str(request.args.get('query')).lower().strip()

    try:
        query = f'''
            SELECT sale.id AS id,
                customer.name AS customer,
                user.name AS salesman,
                STRFTIME('%d/%m/%Y', sale.sell_date) AS sell_date,
                sale.total AS total
            FROM sales sale 
                INNER JOIN customers customer ON sale.customer_id = customer.id
                INNER JOIN users user on sale.salesman_id = user.id
            WHERE sale.id LIKE '{searched}' OR
                customer.name LIKE '%{searched}%' OR
                customer.cpf LiKE '%{searched}%' OR
                user.name LIKE '%{searched}%'
            ORDER BY sale.id ASC;
        '''

        sales = db.session.execute(text(query)).all()

        sales_list = []
        if sales:
            sales_list.extend([
                {
                    'id' : sale.id,
                    'customer' : str(sale.customer).title(),
                    'salesman' : str(sale.salesman).title(),
                    'sell_date' : sale.sell_date,
                    'total' : sale.total
                }
                for sale in sales
            ])
        return jsonify({'sales' : sales_list})
    except Exception as e:
        print(e)
        flash(f'Erro ao pesquisar venda - {e}')
        return redirect(url_for('sales.render_page'))


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