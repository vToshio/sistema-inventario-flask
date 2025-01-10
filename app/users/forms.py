from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length
from app.models import db, UserRole

class NewUserForm(FlaskForm):
    name = StringField('Nome', id='nome-adicionar-usuario', name='nome-adicionar-usuario', validators=[DataRequired(), Length(max=50)])
    username = StringField('Username', id='username-adicionar-usuario', name='username-adicionar-usuario', validators=[DataRequired(), Length(max=20)])
    role_id = SelectField('Cargo', id='select-cargo-adicionar-usuario', name='select-cargo-adicionar-usuario', choices=[], validators=[DataRequired()])
    email = EmailField('Email', id='email-adicionar-usuario', name='email-adicionar-usuario', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Senha', id='senha-adicionar-usuario', name='senha-adicionar-usuario', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha', id='confirmar-adicionar-usuario', name='confirmar-adicionar-usuario')
    submit = SubmitField('Adicionar Usuário')

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.desc) for role in db.session.query(UserRole).all() if role.desc != 'master']

class ChangePasswdForm(FlaskForm):
    new_password = PasswordField()
    confirm = PasswordField()
    submit = SubmitField()

class EditUserForm(FlaskForm):
    id = HiddenField()
    name = StringField()
    username = StringField()
    role = SelectField()
    email = EmailField()
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.desc) for role in db.session.query(UserRole).all()]


class DeleteUserForm(FlaskForm):
    id = HiddenField()
    submit = SubmitField()