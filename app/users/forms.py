from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length

class NewUserForm(FlaskForm):
    pass

class ChangePasswdForm(FlaskForm):
    pass

class EditUserForm(FlaskForm):
    pass

class DeleteUserForm(FlaskForm):
    pass