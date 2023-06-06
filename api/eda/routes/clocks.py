import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Blueprint, current_app, render_template, request, session

from sateda.dbconnector.mongo import MongoDB

from ..utilities import init_page, extra

clocks_bp = Blueprint('clocks', __name__)

@clocks_bp.route('/clocks', methods=['GET', 'POST'])
def clocks():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return init_page(template="clocks.jinja")
    
def handle_post_request():
    return ""