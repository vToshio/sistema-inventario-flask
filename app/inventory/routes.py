from flask import Blueprint, render_template, redirect, jsonify, url_for, flash, get_flashed_messages, request, session
from app.models import db, Product, ProductCategory
from app.helpers import login_required
from app.inventory.forms import *

inventory = Blueprint('inventory', __name__)

@inventory.route('/sistema/home/estoque', methods=['GET'])
@login_required
def render_page():
    '''
    Métodos:
    - GET: Renderiza a página de gerenciamento do estoque.
    '''
   
    products = Product.query.first()
    categories = ProductCategory.query.all()
        
    new_product = NewProductForm()
    add_units = AddUnitsForm()
    edit_product = EditProductForm()
    delete_product = DeleteProductForm()
    new_category = NewCategoryForm()
    delete_category = DeleteCategoryForm()
        
    messages = get_flashed_messages()

    return render_template(
        'estoque.html',
        pagetitle='Estoque',
        new_product=new_product,
        add_units=add_units,
        edit_product=edit_product,
        delete_product=delete_product,
        new_category=new_category,
        delete_category=delete_category, 
        messages=messages, 
        categories=categories, 
        products=products, 
        session=session
    )

@inventory.route('/api/products', methods=['GET'])
@login_required
def get_products():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    prod_list = [
        {
            'id' : product.id,
            'desc' : product.desc.title(),
            'category_id' : product.category.id,
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
        }
    )

@inventory.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    categories = ProductCategory.query.all()

    cat_list = [
        {
            'id' : category.id,
            'desc' : category.desc.title()
        }
        for category in categories
    ]

    return jsonify({'categories' : cat_list})


@inventory.route('/api/products/search', methods=['GET'])
@login_required
def search_products():
    query = request.args.get('query', default='')

    products = Product.query.join(ProductCategory).filter(
        ((Product.id == query) |
        (Product.desc == query.lower()) |
        (ProductCategory.desc == query.lower()) |
        (Product.price == query) |
        (Product.quantity == query))
    ).all()

    prod_list = [
        {
            'id': product.id,
            'desc' : product.desc.title(),
            'category_id' : product.category.id,
            'category' : product.category.desc.title(),
            'quantity' : product.quantity,
            'price' : product.price
        }
        for product in products
    ]

    return jsonify({'products' : prod_list})


@inventory.route('/api/products/new', methods=['POST'])
@login_required
def new_product():
    form = NewProductForm()
    
    if form.validate_on_submit():
        desc = form.desc.data
        category = form.category_id.data
        price = form.price.data

        if Product.query.filter_by(desc=desc).first():
            flash(f'Produto com o nome "{desc}" já cadastrado.')
        else:
            try:
                db.session.add(Product(
                    desc = str(desc).strip().lower(), 
                    category_id = int(category), 
                    price = float(price), 
                    quantity = 0)
                )
                db.session.commit()
                flash(f'Produto "{desc}" cadastrado com sucesso!')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro no cadastro do produto - {e}')
    else:
        flash('Todos os campos devem estar preenchidos.')
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/products/add-units', methods=['POST'])
@login_required
def add_units():
    form = AddUnitsForm()
    
    if form.validate_on_submit():
        id = form.id.data
        units = form.units.data
    
        product = Product.query.filter_by(id=id).first()
        
        if not product:
            flash('Produto não encontrado na base de dados.')
        else:
            try:
                product = db.session.query(Product).filter_by(id=id).first()
                product.quantity += units
                db.session.commit()
                flash(f'{units} adicionadas ao produto "{product.desc}".')
            except Exception as e:
                flash(f'Erro ao adicionar unidades - {e}')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('inventory.render_page'))

@inventory.route('/api/products/edit', methods=['POST'])
@login_required
def edit_product():
    form = EditProductForm()

    if form.validate_on_submit():
        id = form.id.data
        desc = form.desc.data
        price = form.price.data
        category_id = form.category.data

        product = Product.query.filter_by(id=id).first()

        try:
            if not product:
                flash(f'Produto "{desc}" não encontrado na base de dados')
            else:
                product.desc = desc
                product.price = price
                product.category_id = category_id
                db.session.commit()
                flash(f'Alterações no produto de ID {id} realizadas com sucesso!')
        except Exception as e:
            flash(f'Erro na alteração de dados do produto - {e}')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/products/delete', methods=['POST'])
@login_required
def delete_product():
    form = DeleteProductForm()
    
    if form.validate_on_submit():
        id = form.id.data

        product = Product.query.filter_by(id=id).first()
        desc = product.desc

        if not product:
            flash('Produto não encontrado no banco de dados.')
        else:
            try:
                db.session.query(Product).filter_by(id=id).delete()
                db.session.commit()
                flash(f'Produto "{desc}" deletado com sucesso!')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao deletar produto - {e}')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/categories/new', methods=['POST'])
@login_required
def new_category():
    form = NewCategoryForm()

    if form.validate_on_submit():
        desc = str(form.desc.data).strip().lower()
        
        try:
            if ProductCategory.query.filter_by(desc=desc).first():
                flash(f'Categoria com a descrição "{desc}" já foi cadastrada.')
            else:
                db.session.add(ProductCategory(desc=desc))
                db.session.commit()
                flash(f'Categoria "{desc}" cadastrada com sucesso!')
        except ValueError:
            flash('Campos com valores inválidos.')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro de categoria - {e}')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/categories/delete', methods=['POST'])
@login_required
def delete_category():
    form = DeleteCategoryForm()

    if form.validate_on_submit():
        id = form.id.data

        try:    
            category = ProductCategory.query.filter_by(id=id).first()
            desc = category.desc
            if not category:
                flash('Categoria não existente no banco de dados.')
            elif Product.query.filter_by(category_id=id).first():
                flash('Não é possível deletar essa categoria pois ela ainda possuí produtos associados à ela.')
            else: 
                db.session.query(ProductCategory).filter_by(id=id).delete()
                db.session.commit()
                flash(f'Categoria "{desc}" deletada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro na deleção de categoria - {e}')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'Erro no campo {field}: {e}')
    return redirect(url_for('inventory.render_page'))