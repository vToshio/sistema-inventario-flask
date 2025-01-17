from flask_wtf import FlaskForm
from wtforms import HiddenField, EmailField, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length
from app.models import db

class NewCustomerForm(FlaskForm):
    name = StringField('Nome do Cliente', id='nome-cadastrar-cliente', name='nome-cadastrar-cliente', validators=[DataRequired(), Length(max=30)])
    email = EmailField('Email', id='email-cadastrar-cliente',name='email-cadastrar-cliente', validators=[DataRequired(), Length(max=50)])
    address = StringField('Endereço', id='endereco-cadastrar-cliente', name='endereco-cadastrar-cliente', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Cadastrar Cliente')

class DeleteCustomerForm(FlaskForm):
    id = IntegerField('ID do cliente', id='id-deletar-cliente', name='id-deletar-cliente', validators=[DataRequired()])
    submit = SubmitField('Deletar Cliente')

class EditCustomerForm(FlaskForm):
    id = HiddenField(id='id-editar-cliente', name='id-editar-cliente')
    name = StringField('Nome do Cliente', id='nome-editar-cliente', name='nome-editar-cliente', validators=[DataRequired(), Length(max=30)])
    email = EmailField('Email', id='email-editar-cliente',name='email-editar-cliente', validators=[DataRequired(), Length(max=50)])
    address = StringField('Endereço', id='endereco-editar-cliente', name='endereco-editar-cliente', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Editar Cliente')
