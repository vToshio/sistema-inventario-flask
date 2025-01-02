from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, SubmitField, HiddenField, validators
from models import db, ProductCategory

class Login(FlaskForm):
    username = StringField('Usuário', validators=[validators.DataRequired()])
    password = PasswordField('Senha', validators=[validators.DataRequired()])
    submit = SubmitField('Entrar')
    nextpage = HiddenField()

class NewProductRecord(FlaskForm):
    description = StringField('Descrição', validators=[validators.DataRequired(), validators.Length(max=100)])
    price = FloatField('Preço', validators=[validators.DataRequired()])
    category_id = SelectField('Categoria', choices=[], validators=[validators.DataRequired()])
    submit = SubmitField('Cadastrar Produto')

    def __init__(self, *args, **kwargs):
        super(NewProductRecord, self).__init__(*args, **kwargs)
        self.category_id.choices = [(cat.id, cat.desc) for cat in db.session.query(ProductCategory).all()]