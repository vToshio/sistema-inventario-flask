from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, validators

class Login(FlaskForm):
    username = StringField('Usuário', validators=[validators.DataRequired()])
    password = PasswordField('Senha', validators=[validators.DataRequired()])
    submit = SubmitField('Entrar')
    nextpage = HiddenField()