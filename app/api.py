from flask import Flask, Blueprint, redirect, jsonify, url_for, flash, request, session
from models import db, Product, ProductCategorie

api = Blueprint('api', __name__)

@api.route('/api/products', methods=['GET'])
def get_products():
    if ('logged_user' not in session or session['logged_user'] is None):
        return redirect(url_for('views.home'))

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
def search_products():
    query = request.args.get('query', default='')

    products = Product.query.join(ProductCategorie).filter(
        ((Product.id == query) |
        (Product.desc == query) |
        (ProductCategorie.desc == query))
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