from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length
from app.models import db, UserRole

class NewUserForm(FlaskForm):
    name = StringField()
    username = StringField()
    role_id = SelectField()
    email = EmailField()
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.desc) for role in db.session.query(UserRole).all()]

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