from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, FieldList, FormField, Form
from wtforms.validators import DataRequired
from app.models import User

class ProductForm(Form):
    id = IntegerField('ID do Produto', validators=[DataRequired()])
    quantity = IntegerField('Quantidade', validators=[DataRequired()])

class SaleForm(FlaskForm):
    customer_id = IntegerField('ID do Cliente', validators=[])
    salesman_id = SelectField( 'Vendedor', coerce=int, choices=[], validators=[DataRequired()])
    discount = SelectField('Desconto', coerce=int, choices=[(0, '0%'), (5, '5%'), (10, '10%'), (15, '15%')])
    products = FieldList(FormField(ProductForm), min_entries=1, validators=[DataRequired()])
    submit = SubmitField('Registrar Venda')

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.salesman_id.choices = [(salesman.id, salesman.name) for salesman in User.query.filter_by(role_id=3).all()]