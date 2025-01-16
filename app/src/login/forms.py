from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Usuário', id='username-login', name='username-login', validators=[DataRequired()])
    password = PasswordField('Senha', id='senha-login', name='senha-login', validators=[DataRequired()])
    submit = SubmitField('Entrar')
    nextpage = HiddenField()
