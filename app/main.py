from flask import Flask
from datetime import datetime

from app.models import db, User, UserRole
from app.views import views
from app.helpers import csrf, bcrypt
from app.inventory.routes import inventory
from app.clients.routes import customers
from app.users.routes import users

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(views)
    app.register_blueprint(inventory)
    app.register_blueprint(customers)
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
                name='Master',
                username='master',
                role_id=1, 
                password=bcrypt.generate_password_hash('master123'),
                email='administrador_empresa@email.com', 
                date_created=datetime.now())
            )
            db.session.commit()

    return app