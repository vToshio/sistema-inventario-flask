from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    '''
    Model that defines each user on the 'users' table on database.

    Atributes:
    - id (int)
    - role (string[6])
    - name (string[30])
    - username (string[20])
    - email (string[100])
    - date_created (date)
    '''
    __tablename__ = 'users'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    role = db.Column('role', db.String(6), nullable=False)
    name = db.Column('name', db.String(30), nullable=False)
    username = db.Column('username', db.String(20), nullable=False, unique=True)
    password = db.Column('password', db.String(100), nullable=False)
    email = db.Column('email', db.String(50), unique=True)
    date_created = db.Column('date_created', db.Date, default=datetime.now, nullable=False)

    sales = db.relationship('Sale', back_populates='salesman', foreign_keys='Sale.salesman_id')
    orders = db.relationship('Order', back_populates='salesman', foreign_keys='Order.salesman_id')

    def __repr__(self):
        return f'<User: {self.username}/{self.id}>'

class Product(db.Model):
    '''
    Model that defines the 'products' table.

    Atributes:
    -

    '''
    __tablename__ = 'products'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    desc = db.Column('desc', db.String(100), nullable=False, unique=True)
    quantity = db.Column('quantity', db.Integer(), nullable=False)
    price = db.Column('price', db.Numeric(precision=10, scale=2), nullable=False)
    category = db.Column('category', db.String(30), nullable=False)
    
    sale_products = db.relationship('SaleProducts', back_populates='product', foreign_keys='SaleProducts.product_id')
    order_products = db.relationship('OrderProducts', back_populates='product', foreign_keys='OrderProducts.product_id')

    def __repr__(self):
        return f'<Product: {self.id}>'

class Customer(db.Model):
    __tablename__ = 'customers'   
    id = db.Column('id', db.Integer(), primary_key=True, nullable=False)
    name = db.Column('name', db.String(30), nullable=False) 
    email = db.Column('email', db.String(50), nullable=False)
    address = db.Column('address', db.String(100), nullable=False)
    
    sales = db.relationship('Sale', back_populates='customer', foreign_keys='Sale.customer_id')

    def __repr__(self):
        return f'<Customer: {self.name}/{self.id}>'

class Provider(db.Model):
    __tablename__ = 'providers'
    provider_id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    address = db.Column('address', db.String(100), nullable=False)

    orders = db.relationship('Order', back_populates='provider', foreign_keys='Order.provider_id')

    def __repr__(self):
        return f'<Provider: {self.name}>'

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    total = db.Column('total', db.Numeric(precision=10, scale=2), nullable=False)
    sell_date = db.Column('sell_date', db.Date(), default=datetime.now, nullable=False)
    discount = db.Column('discount', db.Integer(), nullable=True)
    salesman_id = db.Column('salesman_id', db.Integer(), db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column('customer_id', db.Integer(), db.ForeignKey('customers.id'), nullable=False)

    salesman = db.relationship('User', back_populates='sales', foreign_keys=[salesman_id])
    customer = db.relationship('Customer', back_populates='sales', foreign_keys=[customer_id])
    sale_products = db.relationship('SaleProducts', back_populates='sale', foreign_keys='SaleProducts.sale_id')

    def __repr__(self):
        return f'<Sale {self.id}: Customer {self.customer_id}/R${self.total}>'
    


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    order_date = db.Column('order_date', db.Date(), default=datetime.now(), nullable=False)
    total = db.Column('total', db.Numeric(precision=10, scale=2), nullable=False)
    salesman_id = db.Column('salesman_id', db.Integer(), db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column('provider_id', db.Integer(), db.ForeignKey('providers.id'), nullable=False)

    salesman = db.relationship('User', back_populates='orders', foreign_keys=[salesman_id])
    provider = db.relationship('Provider', back_populates='orders', foreign_keys=[provider_id])
    order_products = db.relationship('OrderProducts', back_populates='order', foreign_keys='OrderProducts.order_id')

    def __repr__(self):
        return f'<Order {self.id}: Provider {self.provider_id}/R${self.total} >'
    
   
class SaleProducts(db.Model):
    __tablename__ = 'sale_products'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    sale_id = db.Column('sale_id', db.Integer(), db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column('product_id', db.Integer(), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column('quantity', db.Integer(), nullable=False, default=1)

    sale = db.relationship('Sale', back_populates='sale_products', foreign_keys=[sale_id])
    product = db.relationship('Product', back_populates='sale_products', foreign_keys=[product_id])

    def __repr__(self):
        return f'<SaleProduct {self.id}: Sale {self.sale_id}>'

   
class OrderProducts(db.Model):
    __tablename__ = 'order_products'
    id = db.Column('id', db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    order_id = db.Column('order_id', db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column('product_id', db.Integer(), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column('quantity', db.Integer(), nullable=False, default=1)

    order = db.relationship('Order', back_populates='order_products', foreign_keys=[order_id])
    product = db.relationship('Product', back_populates='order_products', foreign_keys=[product_id])

    def __repr__(self):
        return f'<OrderProducts {self.id}: Order {self.order_id}>'