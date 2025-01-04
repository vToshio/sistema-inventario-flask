from flask import Blueprint, redirect, jsonify, url_for, flash, request, session
from models import db, Product, ProductCategory
from helpers import login_required
from forms import *

api = Blueprint('api', __name__)

@api.route('/api/products', methods=['GET'])
@login_required
def get_products():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    prod_list = [
        {
            'id' : product.id,
            'desc' : product.desc.title(),
            'category' : product.category.desc.title(),
            'quantity' : product.quantity,
            'price' : product.price
        }
        for product in products.items
    ]

    return jsonify(
        {
            'products': prod_list, 
            'page': products.page, 
            'per_page' : per_page, 
            'total' : products.total, 
            'pages': products.pages
        })

@api.route('/api/products/search', methods=['GET'])
@login_required
def search_products():
    query = request.args.get('query', default='')

    products = Product.query.join(ProductCategory).filter(
        ((Product.id == query) |
        (Product.desc == query) |
        (ProductCategory.desc == query))
    ).all()

    prod_list = [
        {
            'id': product.id,
            'desc' : product.desc,
            'category' : product.category.desc,
            'quantity' : product.quantity,
            'price' : product.price
        }
        for product in products
    ]

    return jsonify({'products' : prod_list})

@api.route('/api/products/new', methods=['POST'])
@login_required
def new_product():
    form = NewProductForm()
    
    if form.validate_on_submit():
        desc = form.description.data
        category = form.category_id.data
        price = form.price.data

        if Product.query.filter_by(desc=desc).first():
            flash(f'Produto com o nome "{desc}" já cadastrado.')
        else:
            try:
                db.session.add(Product(desc=desc, category_id=category, price=price, quantity=0))
                db.session.commit()
                flash('Produto cadastrado com sucesso!')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro no cadastro do produto - {e}')
    else:
        flash('Todos os campos devem estar preenchidos.')
    return redirect(url_for('views.inventory'))

@api.route('/api/products/add-units', methods=['POST'])
def add_units():
    try:
        product_id = request.form['id-produto-adicionar']
        units = int(request.form['units-adicionar'])

        product = Product.query.filter_by(id=product_id).first()

        if not product:
            flash('Produto não encontrado na base de dados.')
        elif product_id and units:
            flash('Os campos não podem estar em branco.')
        else:
            product = db.session.query(Product).filter_by(id=product_id).first()
            product.quantity += units
            db.session.commit()
            flash(f'{units} adicionadas ao produto "{product.desc}".')
    except ValueError:
        flash('O campo de quantidade deve ser um valor numérico inteiro (Ex:1, 10, 100...)')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar unidades a um produto: {e}')
    return redirect(url_for('views.inventory'))

@api.route('/api/products/delete', methods=['POST'])
def delete_product():
    try:
        product_id = request.form['id-produto-deletar']
        
        product = Product.query.filter_by(id=product_id).first()
        
        if not product:
            flash('Produto não encontrado no banco de dados.')
        else:
            db.session.query(Product).filter_by(id=product_id).delete()
            db.session.commit()
            flash(f'Produto "{product.desc}" deletado com sucesso!')
    except ValueError as e:
        flash(f'Campos inválidos.')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar produto - {e}')
    return redirect(url_for('views.inventory'))


@api.route('/api/categories/new', methods=['POST'])
def new_category():
    try:
        desc = request.form['desc-categoria-cadastrar'].strip()

        if ProductCategory.query.filter_by(desc=desc).first():
            flash('Categoria já existente no banco de dados.')
        elif desc:
            db.session.add(ProductCategory(desc=desc))
            db.session.commit()
            flash(f'Categoria "{desc}" cadastrada com sucesso.')
        else:
            flash('Não é possível adicionar um campo vazio.')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar categoria - {e}')
    return redirect(url_for('views.inventory'))

@api.route('/api/categories/delete', methods=['POST'])
def delete_category():
    try:
        category_id = request.form['id-categoria-deletar'] 
        
        if not Product.query.filter(Product.category_id == category_id).first():
            ProductCategory.query.filter(ProductCategory.id == category_id).delete()
            db.session.commit()
        else:
            flash('Categoria não pode ser removida: ainda existem produtos com essa categoria.')
    except Exception as e:
        flash(f'Erro ao deletar categoria do banco de dados - {e}')    
    return redirect(url_for('views.inventory'))