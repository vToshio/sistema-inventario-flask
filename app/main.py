from flask import Flask
from datetime import datetime

from app.models import db, User, UserRole, ProductCategory, Customer
from app.src.login.routes import login
from app.helpers import generate_random_password, csrf, bcrypt
from app.src.home.routes import home
from app.src.inventory.routes import inventory
from app.src.customers.routes import customers
from app.src.users.routes import users
from app.src.sales.routes import sales


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(login)
    app.register_blueprint(home)
    app.register_blueprint(inventory)
    app.register_blueprint(customers)
    app.register_blueprint(sales)
    app.register_blueprint(users)
    app.config.from_pyfile('config.py')
    
    with app.app_context():
        csrf.init_app(app)
        bcrypt.init_app(app)
        db.init_app(app)
        db.create_all()

        roles = UserRole.query.all()
        found_master = User.query.filter_by(username='master').first()
        categories = ProductCategory.query.filter_by(id=0).first()
        unregistered_customer = Customer.query.filter_by(id=0).first()

        if not roles:
            db.session.add(UserRole(desc='master'))
            db.session.add(UserRole(desc='admin'))
            db.session.add(UserRole(desc='user'))
            print('Categorias de usuário criadas com sucesso!')

        if not found_master:
            password = generate_random_password()

            db.session.add(User(
                id=0,
                name='Master',
                username='master',
                role_id=1, 
                password=bcrypt.generate_password_hash(password),
                email='administrador_empresa@email.com', 
                date_created=datetime.now())
            )
            print(f'[MASTER-PASSWORD] {password}')

        if not categories:
            db.session.add(ProductCategory(
                id=0,
                desc='Não Registrada')
            )
            print('Categoria "Não Registrada" adicionada!')

        if not unregistered_customer:
            db.session.add(Customer(
                id = 0,
                name = 'Não Registrado',
                cpf = '-',
                email = '-',
                address = '-'
            ))
            print('Usuário "Não Registrado" criado com sucesso!')


        db.session.commit()

    return app