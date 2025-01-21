from flask import Flask
from datetime import datetime

from app.models import db, User, UserRole, ProductCategory
from app.src.login.routes import login
from app.helpers import csrf, bcrypt
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

        found_master = User.query.filter(User.username == 'master').first()
        if not found_master:
            db.session.add(UserRole(desc='master'))
            db.session.add(UserRole(desc='admin'))
            db.session.add(UserRole(desc='user'))
            db.session.add(User(
                id=0,
                name='Master',
                username='master',
                role_id=1, 
                password=bcrypt.generate_password_hash('master123'),
                email='administrador_empresa@email.com', 
                date_created=datetime.now())
            )
            db.session.add(ProductCategory(id=0, desc='Não Registrada'))
            db.session.commit()

    return app