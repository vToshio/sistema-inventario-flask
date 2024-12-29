from flask import Flask
from views import views

app = Flask(__name__)
app.register_blueprint(views)
app.config.from_pyfile('config.py')

if __name__ == '__main__':
    app.run(debug=True)