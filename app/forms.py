from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from models import db, ProductCategory

DATA_REQUIRED_MESSAGE = 'O preenchimento deste campo é obrigatório.'

class LoginForm(FlaskForm):
    username = StringField('Usuário', id='username-login', name='username-login', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    password = PasswordField('Senha', id='senha-login', name='senha-login', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Entrar')
    nextpage = HiddenField()

class NewProductForm(FlaskForm):
    desc = StringField('Descrição', id='desc-cadastrar', name='desc-cadastrar', validators=[DataRequired(DATA_REQUIRED_MESSAGE), Length(max=100)])
    price = FloatField('Preço', id='preco-cadastrar', name='preco-cadastrar', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    category_id = SelectField('Categoria', id='idcategoria-cadastrar', name='idcategoria-cadastrar', choices=[], validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Cadastrar Produto')

    def __init__(self, *args, **kwargs):
        super(NewProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(cat.id, cat.desc) for cat in db.session.query(ProductCategory).all()]

class AddUnitsForm(FlaskForm):
    id = HiddenField(name='id-produto-adicionar', id='id-produto-adicionar')
    units = IntegerField('Quantidade', name='units-adicionar', id='units-adicionar', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Adicionar Unidades')

class EditProductForm(FlaskForm):
    id = HiddenField(id='id-produto-editar', name='id-produto-editar')
    desc = StringField('Descrição', id='desc-produto-editar', name='desc-produto-editar', validators=[DataRequired(DATA_REQUIRED_MESSAGE), Length(max=100)])
    price = FloatField('Preço', id='preco-produto-editar', name='preco-produto-editar', validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    category = SelectField('Categoria', id='select-categoria-editar', coerce=int, name='select-categoria-editar', choices=[], validators=[DataRequired(DATA_REQUIRED_MESSAGE)])
    submit = SubmitField('Editar Produto')

    def __init__(self, *args, **kwargs):
        super(EditProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(cat.id, cat.desc) for cat in db.session.query(ProductCategory).all()]


class DeleteProductForm(FlaskForm):
    id = HiddenField(id='id-produto-deletar', name='id-produto-deletar')
    submit = SubmitField('Deletar Produto')

class NewCategoryForm(FlaskForm):
    desc = StringField('Descrição', id='desc-categoria-cadastrar', name='desc-categoria-cadastrar', validators=[DataRequired(DATA_REQUIRED_MESSAGE), Length(max=20)])
    submit = SubmitField('Cadastrar Categoria')

class DeleteCategoryForm(FlaskForm):
    id = HiddenField(id='id-categoria-deletar', name='id-categoria-deletar')
    submit = SubmitField('Deletar Categoria')