import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from flask import Blueprint, current_app, render_template, request, session

from sateda.data.measurements import MeasurementArray, Measurements
from sateda.dbconnector.mongo import MongoDB

# eda_bp = Blueprint('eda', __name__)

states_bp = Blueprint('states', __name__)
plotType = ["Scatter", "Line"]

@states_bp.route('/states', methods=['GET', 'POST'])
def states():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return init()
    
def handle_post_request():
    return

def init():
    connect_db_ip = session["mongo_ip"]
    db_name = session["mongo_db"]
    db_port = session["mongo_port"]
    print(connect_db_ip, db_name)
    #TODO Later, database content, can be loaded in the session
    client = MongoDB(url=connect_db_ip, port=db_port, data_base=db_name)
    client.connect()
    client.get_content()
    return render_template("states.jinja", content=client.mongo_content, plot_type=plotType, exlcude=0)
    
