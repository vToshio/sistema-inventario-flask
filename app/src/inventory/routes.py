from flask import Blueprint, render_template, redirect, jsonify, url_for, flash, get_flashed_messages, request, session
from app.models import db, Product, ProductCategory
from app.helpers import login_required, flash_messages
from app.src.inventory.forms import *

inventory = Blueprint('inventory', __name__)

@inventory.route('/sistema/home/estoque', methods=['GET'])
@login_required
def render_page():
    '''
    Renderiza a página de gerenciamento de estoque.
    '''
    products = Product.query.first()
    categories = ProductCategory.query.all()        

    return render_template(
        'estoque.html',
        pagetitle='Estoque',
        new_product = NewProductForm(),
        add_units = AddUnitsForm(),
        edit_product = EditProductForm(),
        delete_product = DeleteProductForm(),
        new_category = NewCategoryForm(),
        delete_category = DeleteCategoryForm(), 
        messages = get_flashed_messages(), 
        categories = categories, 
        products = products, 
        session = session
    )

@inventory.route('/api/products', methods=['GET'])
@login_required
def get_products():
    '''
    Rota da API que retorna uma lista de produtos paginados através de um request por método GET.

    Query args:
    - page (int): Define a página de produtos em que a tabela se localiza
    - per_page (int): define quantos produtos serão renderizados por página

    Retorno:
    - JSON contendo:
        - 'products' (list): lista de produtos
        - 'page' (int): página atual
        - 'per_page' (int): quantidade de produtos por página
        - 'total' (int): quantidade total de produtos
        - 'pages' (int): quantidade total de páginas
    '''
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
    '''
    Rota da API que retorna uma lista de categorias ao receber uma request por método GET.

    Retorno:
    - JSON contendo:
        - 'categories' (list): lista de categorias de produtos
    '''
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
    '''
    Rota da API que retorna uma lista com todos os produtos identificados por uma query string.

    Query Args:
    - query (str): string que identifica um produto por id, descrição, preço ou quantidade

    Retorno:
    - JSON contendo:
        - 'products' (list): lista de produtos identificados pela query string
    '''
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
    '''
    Rota da API que registra no banco de dados um novo produto, através do método POST.
    
    Dados Coletados NewProductForm:
    - desc (str): descrição do produto
    - category (int): id de identicação de categoria de um produto
    - price (float): valor do produto
    '''

    form = NewProductForm()
    
    if form.validate_on_submit():
        desc = form.desc.data
        category = form.category_id.data
        price = form.price.data

        try:
            if Product.query.filter_by(desc=desc).first():
                raise Exception(f'Produto com o nome "{desc.title()}" já cadastrado.')
        
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
    '''
    Rota da API que adiciona unidades à um produto já cadastrado, por meio do método POST.

    Dados AddUnitsForm:
    - id (int): id de identificação do produto
    - units (int): quantidade de unidades adicionadas ao estoque
    '''
    form = AddUnitsForm()
    
    if form.validate_on_submit():
        id = form.id.data
        units = form.units.data
    
        try:
            product = Product.query.filter_by(id=id).first()
        
            if not product:
                raise Exception('Produto não encontrado na base de dados.')
       
            product = db.session.query(Product).filter_by(id=id).first()
            product.quantity += units
            db.session.commit()
            flash(f'{units} adicionadas ao produto "{product.desc.title()}".')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar unidades - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('inventory.render_page'))

@inventory.route('/api/products/edit', methods=['POST'])
@login_required
def edit_product():
    '''
    Rota da API que redefine os dados de um produto (já cadastrado), por meio do método POST.

    Dados alterados:
    - desc (str): descrição do produto
    - price (float): preço do produto
    - category_id (int): id da categoria do produto
    '''
    form = EditProductForm()

    if form.validate_on_submit():
        id = form.id.data
        desc = form.desc.data
        price = form.price.data
        category_id = form.category.data

        try:
            product = Product.query.filter_by(id=id).first()

            if not product:
                raise Exception(f'Produto "{desc}" não encontrado na base de dados')
            
            product.desc = desc
            product.price = price
            product.category_id = category_id
            db.session.commit()
            flash(f'Alterações no produto de ID {id} realizadas com sucesso!')
        except Exception as e:
            flash(f'Erro na alteração de dados do produto - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/products/delete', methods=['POST'])
@login_required
def delete_product():
    '''
    Rota da API que deleta um produto do banco de dados, por método POST.
    '''
    form = DeleteProductForm()
    
    if form.validate_on_submit():
        id = form.id.data
        try:
            product = Product.query.filter_by(id=id).first()

            if not product:
                raise Exception('Produto não cadastrado no banco de dados.')
            elif product.quantity > 0:
                raise Exception('Ainda há unidades deste produto em estoque.')
            
            desc = product.desc
            db.session.query(Product).filter_by(id=id).delete()
            db.session.commit()
            flash(f'Produto "{desc}" deletado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao deletar produto - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/categories/new', methods=['POST'])
@login_required
def new_category():
    '''
    Rota da API que registra uma nova categoria, através do método POST.

    Dados cadastrado por categoria:
    - desc (str): descrição da categoria
    '''
    form = NewCategoryForm()

    if form.validate_on_submit():
        desc = str(form.desc.data).strip().lower()
        
        try:
            if ProductCategory.query.filter_by(desc=desc).first():
                raise Exception(f'Categoria com a descrição "{desc}" já foi cadastrada.')
            
            db.session.add(ProductCategory(desc=desc))
            db.session.commit()
            flash(f'Categoria "{desc}" cadastrada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no cadastro de categoria - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('inventory.render_page'))


@inventory.route('/api/categories/delete', methods=['POST'])
@login_required
def delete_category():
    '''
    Rota da API que deleta uma categoria do banco de dados, por método POST.
    '''
    form = DeleteCategoryForm()

    if form.validate_on_submit():
        id = form.id.data

        try:    
            category = ProductCategory.query.filter_by(id=id).first()
            desc = category.desc
            
            if not category:
                raise Exception('Categoria não existente no banco de dados.')
            elif Product.query.filter_by(category_id=id).first():
                raise Exception('Não é possível deletar essa categoria pois ela ainda possuí produtos associados à ela.')
            
            db.session.query(ProductCategory).filter_by(id=id).delete()
            db.session.commit()
            flash(f'Categoria "{desc}" deletada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro na deleção de categoria - {e}')
    else:
        flash_messages(form.errors)
    return redirect(url_for('inventory.render_page'))