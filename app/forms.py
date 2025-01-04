from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from models import db, ProductCategory

DATA_REQUIRED_MESSAGE = 'O preenchimento deste campo é obrigatório.'

class LoginForm(FlaskForm):
    username = StringField('Usuário', id='username-login', name='username-login', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    password = PasswordField('Senha', id='senha-login', name='senha-login', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Entrar')
    nextpage = HiddenField()

class NewProductForm(FlaskForm):
    description = StringField('Descrição', id='desc-cadastrar', name='desc-cadastrar', validators=[DataRequired(DATA_REQUIRED_MESSAGE), Length(max=100)])
    price = FloatField('Preço', id='preco-cadastrar', name='preco-cadastrar', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    category_id = SelectField('Categoria', id='idcategoria-cadastrar', name='idcategoria-cadastrar', choices=[], validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Cadastrar Produto')

    def __init__(self, *args, **kwargs):
        super(NewProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(cat.id, cat.desc) for cat in db.session.query(ProductCategory).all()]

class EditProductForm(FlaskForm):
    pass    

class DeleteProductForm(FlaskForm):
    pass

class NewCategoryForm(FlaskForm):
    pass

class DeleteCategoryForm(FlaskForm):
    pass