from flask import Flask
from datetime import datetime
from models import db, User
from views import views, bcrypt
from helpers import csrf
from api import api

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(views)
    app.register_blueprint(api)
    app.config.from_pyfile('config.py')
    
    with app.app_context():
        csrf.init_app(app)
        bcrypt.init_app(app)
        db.init_app(app)
        db.create_all()

        found_master = User.query.filter(User.username == 'master').first()
        if not found_master:
            db.session.add(User(
                name='Master',
                username='master',
                role='master', 
                password=bcrypt.generate_password_hash('master123'),
                email='administrador_empresa@email.com', 
                date_created=datetime.now())
            )
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)