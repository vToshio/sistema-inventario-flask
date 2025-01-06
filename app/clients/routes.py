from flask import Blueprint, render_template, flash, get_flashed_messages, redirect, url_for, get_flashed_messages, session, request
from app.helpers import login_required
from app.models import Customer, db

clients = Blueprint('clients', __name__)

@clients.route('/sistema/home/clientes', methods=['GET'])
@login_required
def render_page():
    return render_template('clientes.html', pagetitle='Clientes', session=session)

@clients.route('/api/clients')
@login_required
def get_clients():
    pass
