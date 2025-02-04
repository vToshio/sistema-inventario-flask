from flask import Blueprint, render_template, redirect, jsonify, abort, url_for, flash, get_flashed_messages, request, session
from app.helpers import login_required, flash_messages, adm_required
from app.models import db, Product, ProductCategory
from werkzeug.exceptions import HTTPException
from app.src.inventory.forms import *
from sqlalchemy import text

inventory = Blueprint('inventory', __name__)

@inventory.route('/sistema/home/estoque', methods=['GET'])
@login_required
def render_page():
    '''
    Renderiza a página de gerenciamento de estoque.
    '''
    products = Product.query.first()
    categories = [cat for cat in ProductCategory.query.all() if cat.id]        

    return render_template(
        'estoque.html',
        pagetitle='Estoque',
        new_product = NewProductForm(),
        add_units = AddUnitsForm(),
        edit_product = EditProductForm(),
        enable_product = EnableProductForm(),
        disable_product = DisableProductForm(),
        new_category = NewCategoryForm(),
        delete_category = DeleteCategoryForm(), 
        messages = get_flashed_messages(), 
        categories = categories, 
        products = products, 
        session = session
    )

@inventory.route('/api/products/<int:id>', methods=['GET'])
@login_required
def get_product(id: int):
    '''
    Rota da API que retorna os dados de um produto através de um request por método GET

    ARGS:
    - id (int): id de um produto

    RETORNO:
    - Json contendo:
        - id (int): id do produto
        - desc (str): descrição do produto
        - price (float): valor do produto
        - category_id (int): id da categoria de um produto
    '''
    if not isinstance(id, int):
        abort('Parâmetro não é um inteiro.')
    
    try:

        product = Product.query.filter_by(id=id).first()

        if not product: 
            raise Exception('Produto não encontrado no banco de dados.')
            

        return jsonify({
            'product' : {
                'id' : product.id,
                'desc' : str(product.desc).title(),
                'price' : product.price,
                'category_id' : product.category_id
            }
        }), 200
    except HTTPException as e:
        print(e)
        flash(f'Erro ao obter produto - {e.description}')
        return redirect(url_for('inventory.render_page'))

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
        - 'products' (list): lista de dicionários com informações de um produto
            - id (int): ID do produto
            - desc (str): Descrição do Produto
            - status (int): estado de disponibilidade do produto
            - category_id (int): ID da categoria do produto
            - category (str): descrição da categoria do produto
            - quantity (int): quantidade de produtos no estoque
            - price (float): preço do produto contendo 2 casas decimais
        - 'page' (int): página atual
        - 'on_screen' (int): quantidade de produtos renderizados na página
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
            'status' : product.status,
            'category_id' : product.category.id,
            'category' : product.category.desc.title(),
            'quantity' : product.quantity,
            'price' : round(product.price, 2)
        }
        for product in products.items if product.status
    ]
    prod_list.reverse()

    return jsonify(
        {
            'products': prod_list,
            'on_screen': len(prod_list), 
            'page': products.page, 
            'per_page' : per_page, 
            'total' : products.total, 
            'pages': products.pages
        }
    ), 200

@inventory.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    '''
    Rota da API que retorna uma lista de categorias ao receber uma request por método GET.

    Retorno:
    - JSON contendo:
        - 'categories' (list): lista de categorias de produtos
            - id (int): ID da categoria
            - desc (str): descrição da categoria
    '''
    categories = ProductCategory.query.all()

    cat_list = [
        {
            'id' : category.id,
            'desc' : category.desc.title()
        }
        for category in categories if category.id
    ]

    return jsonify({'categories' : cat_list}), 200


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
            - id (int): ID do produto
            - desc (str): Descrição do Produto
            - status (int): estado de disponibilidade do produto
            - category_id (int): ID da categoria do produto
            - category (str): descrição da categoria do produto
            - quantity (int): quantidade de produtos no estoque
            - price (float): preço do produto contendo 2 casas decimais
    '''
    searched = request.args.get('query', default='')

    try:
        query = f"""
            SELECT prod.id as id, 
                prod.desc as desc,
                prod.category_id as category_id,
                prod.status as status,
                cat.desc as category,
                prod.quantity as quantity,
                ROUND(prod.price, 2) as price
            FROM products prod
            INNER JOIN product_categories cat ON prod.category_id = cat.id
            WHERE prod.id LIKE '{searched}' OR
                prod.desc LIKE '%{searched.lower()}%' OR
                cat.desc LIKE '%{searched.lower()}%'
            ORDER BY prod.id ASC;   
        """
        products = db.session.execute(text(query)).all()
        
        prod_list = []
        if products:
            prod_list.extend([
                {
                    'id': product.id,
                    'desc' : product.desc.title(),
                    'category_id' : product.category_id,
                    'status' : product.status,
                    'category' : product.category.title(),
                    'quantity' : product.quantity,
                    'price' : round(product.price, 2)
                }
                for product in products
            ])
        return jsonify({'products' : prod_list}), 200
    except Exception as e:
        print(e)
        flash(f'Erro ao realizar pesquisa de produto - {e}')
        return redirect(url_for('inventory.render_page'))

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


@inventory.route('/api/products/add-units/<int:id>', methods=['PATCH'])
@login_required
def add_units(id: int):
    '''
    Rota da API que adiciona unidades à um produto já cadastrado, por meio do método PATCH.

    Dados AddUnitsForm:
    - id (int): id de identificação do produto
    - units (int): quantidade de unidades adicionadas ao estoque
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do produto deve ser um inteiro positivo.'})
    
    form = AddUnitsForm(data=request.get_json())
    
    if form.validate():
        units = form.units.data
        try:
            if units < 0:
                abort(400, 'A quantidade de unidades adicionadas deve ser positiva.')

            product = db.session.query(Product).filter_by(id=id).first()

            if not product:
                abort(404, 'Produto não encontrado na base de dados.')
            elif not product.status:
                raise abort(403, 'Não é possível adicionar unidades de produtos desativados. ')

            product.quantity += units
            db.session.commit()
            return jsonify({'message' : f'{units} adicionadas ao produto "{product.desc.title()}".'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao adicionar unidades - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@inventory.route('/api/products/edit/<int:id>', methods=['PUT'])
@login_required
@adm_required(route='inventory.render_page')
def edit_product(id: int):
    '''
    Rota da API que redefine os dados de um produto (já cadastrado), por meio do método PUT.

    Dados alterados:
    - desc (str): descrição do produto
    - price (float): preço do produto
    - category_id (int): id da categoria do produto
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do produto deve ser um inteiro positivo.'})
    
    form = EditProductForm(data=request.get_json())

    if form.validate():
        desc = form.desc.data
        price = form.price.data
        category_id = form.category_id.data

        try:
            product = Product.query.filter_by(id=id).first()

            if not product:
                abort(404, f'Produto "{desc}" não encontrado na base de dados')
            elif not product.status:
                abort(403, 'Não é possível editar um produto desativado.')


            product.desc = desc
            product.price = price
            product.category_id = category_id
            db.session.commit()
            return jsonify({'message' : f'Alterações no produto de ID {id} realizadas com sucesso!'}), 200
        except HTTPException as e:
            return jsonify({'message' : f'Erro na alteração de dados do produto - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@inventory.route('/api/products/enable-status/<int:id>', methods=['PATCH'])
@adm_required(route='inventory.render_page')
@login_required
def enable_product(id: int):
    '''
    Rota da API que reativa um produto no estoque por método PATCH.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do produto deve ser um inteiro positivo.'})
    
    form = EnableProductForm(data=request.get_json())

    if form.validate():
        try:
            product = Product.query.filter_by(id=id).first()

            if not product:
                abort(404, f'Produto não cadastrado no banco de dados.')
            elif product.status:
                abort(403, f'Produto de ID {id} já está ativo.')
            
            product.status = 1
            db.session.commit()
            return jsonify({'message' : f'Produto "{product.desc.title()}" reativado com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao reativar produto - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400

@inventory.route('/api/products/disable-status/<int:id>', methods=['PATCH'])
@adm_required(route='inventory.render_page')
@login_required
def disable_product(id: int):
    '''
    Rota da API que muda o status de um produto para inativo, por método POST.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID do produto deve ser um inteiro positivo.'})
    
    form = DisableProductForm(data=request.get_json())
    
    if form.validate():
        try:
            product = Product.query.filter_by(id=id).first()

            if not product:
                abort(404, 'Produto não cadastrado no banco de dados.')
            elif not product.status:
                abort(403, f'O Produto de ID {id} já está desativado.')
            elif product.quantity > 0:
                abort(403, 'Ainda há unidades deste produto em estoque.')
            
            product.status = 0
            db.session.commit()
            return jsonify({'message' : f'Produto "{product.desc.title()}" desativado com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro ao desativar produto - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'}), 400
    


@inventory.route('/api/categories/new', methods=['POST'])
@login_required
@adm_required(route='inventory.render_page')
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


@inventory.route('/api/categories/delete/<int:id>', methods=['DELETE'])
@login_required
@adm_required(route='inventory.render_page')
def delete_category(id: int):
    '''
    Rota da API que deleta uma categoria do banco de dados, por método DELETE.
    '''
    if not isinstance(id, int) or id<0:
        return jsonify({'message' : 'O ID da categoria deve ser um inteiro positivo.'})

    form = DeleteCategoryForm(data=request.get_json())

    if form.validate():
        try:    
            if not id:
                abort(403, 'Essa categoria não pode ser deletada') 
            
            category = ProductCategory.query.filter_by(id=id).first()
            if not category:
                abort(404, 'Categoria não existente no banco de dados.')
            
            products = Product.query.filter_by(category_id=category.id).all()
            enabled_products = [product for product in products if product.status]
            if enabled_products:
                abort(403, 'Não é possível deletar essa categoria pois ela ainda possui produtos ativos.')
            
            for prod in products:
                prod.category_id = 0

            desc = category.desc
            db.session.query(ProductCategory).filter_by(id=id).delete()
            db.session.commit()
            return jsonify({'message' : f'Categoria "{desc}" deletada com sucesso!'}), 200
        except HTTPException as e:
            db.session.rollback()
            return jsonify({'message' : f'Erro na deleção de categoria - {e.description}'}), e.code
    return jsonify({'message' : 'Todos os campos devem estar preenchidos.'})