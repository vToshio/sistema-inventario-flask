from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, IntegerField, PasswordField, SubmitField, HiddenField, SelectField
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
    id = HiddenField(id='id-mudar-senha', name='id-mudar-senha', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', id='nova-senha-usuario', name='nova-senha-usuario', validators=[DataRequired(), Length(min=10, max=100)])
    confirm = PasswordField('Confirmar Nova Senha', id='confirmar-nova-senha', name='confirmar-nova-senha', validators=[DataRequired(), Length(min=10, max=100)])

class EditUserForm(FlaskForm):
    id = HiddenField(id='id-editar-usuario', name='id-editar-usuario', validators=[DataRequired()])
    name = StringField('Nome Completo', id='nome-editar-usuario', name='nome-editar-usuario', validators=[DataRequired(), Length(max=50)])
    username = StringField('Nome de Acesso', id='username-editar-usuario', name='username-editar-usuario', validators=[DataRequired(), Length(max=20)])
    email = EmailField('E-mail', id='email-editar-usuario', name='email-editar-usuario', validators=[DataRequired(), Length(max=50)])
    
class EditRoleForm(FlaskForm):
    id = HiddenField(id='id-editar-cargo', name='id-editar-cargo', validators=[DataRequired()])
    role_id = SelectField('Cargo', id='select-editar-cargo', name='select-editar-cargo', choices=[], validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(EditRoleForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.desc) for role in db.session.query(UserRole).all() if role.desc != 'master']


class EnableStatusForm(FlaskForm):
    id = IntegerField('ID do Usuário', id='id-ativar-status', name='id-ativar-status', validators=[DataRequired()])

class DisableStatusForm(FlaskForm):
    id = HiddenField(id='id-desativar-status', name='id-desativar-status', validators=[DataRequired()])