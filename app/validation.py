from flask import Blueprint, redirect, url_for, flash, request, session
from flask_bcrypt import Bcrypt
from models import *

val = Blueprint('val', __name__)
bcrypt = Bcrypt()

@val.route('/login/validate', methods=['POST'])
def login_validation():
    next = request.form['nextpage']
    username = request.form['username']
    passwd = request.form['password']
    
    found_user = User.query.filter(User.username == username).first()
    if found_user:
        if bcrypt.check_password_hash(found_user.password, passwd):
            session['logged_user'] = username
            session['user_role'] = found_user.role
            return redirect(url_for('views.home'))
        flash('Senha incorreta.', 'error')
    else:
        flash('Usuário ainda não cadastrado.', 'error')
    return redirect(url_for('views.login', next=next))

@val.route('/products/new-product', methods=['POST'])
def new_product():
    desc = request.form['description'].strip()
    category = request.form['category_id']
    price = request.form['price']
    print(desc, category, price)

    if Product.query.filter_by(desc=desc).first():
        flash('Já existe um produto cadastrado com essa descrição.')
    elif desc and price and category:
        db.session.add(Product(desc=desc, category_id=category, quantity=0, price=price))
        db.session.commit()
    else:
        flash('Os campos de descrição e preço não podem estar vazios.')
    return redirect(url_for('views.inventory'))

@val.route('/products/delete-product', methods=['POST'])
def delete_product():
    product_id = request.form['id-produto-delete']
    if not Product.query.filter_by(id=product_id).first():
        flash('Produto não encontrado na base de dados.')
    else:
        db.session.query(Product).filter_by(id=product_id).delete()
        db.session.commit()
    return redirect(url_for('views.inventory'))

@val.route('/products/new-category', methods=['POST'])
def new_category():
    desc = request.form['new_category'].strip()

    if ProductCategory.query.filter_by(desc=desc).first():
        flash('Categoria já existente no banco de dados.')
    elif desc:
        db.session.add(ProductCategory(desc=desc))
        db.session.commit()
    else:
        flash('Não é possível adicionar um campo vazio.')

    return redirect(url_for('views.inventory'))

@val.route('/products/delete-category', methods=['POST'])
def delete_category():
    category_id = request.form['id-categoria-delete'] 
    
    if not Product.query.filter(Product.category_id == category_id).first():
        ProductCategory.query.filter(ProductCategory.id == category_id).delete()
        db.session.commit()
    else:
        flash('Categoria não pode ser removida: ainda existem produtos com essa categoria.')
    return redirect(url_for('views.inventory'))
    