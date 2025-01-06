from flask_wtf import FlaskForm
from wtforms import HiddenField, EmailField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import db

class NewCustomerForm(FlaskForm):
    name = StringField('Nome do Cliente', id='nome-cadastrar-cliente', name='nome-cadastrar-cliente', validators=[DataRequired(), Length(max=30)])
    email = EmailField('Email', id='email-cadastrar-cliente',name='email-cadastrar-cliente', validators=[DataRequired(), Length(max=50)])
    address = StringField('Endereço', id='endereco-cadastrar-cliente', name='endereco-cadastrar-cliente', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Cadastrar Cliente')