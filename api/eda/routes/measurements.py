from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB
import numpy as np
# eda_bp = Blueprint('eda', __name__)

measurements_bp = Blueprint('measurements', __name__)
plotType = ["Scatter", "Line"]

@measurements_bp.route('/measurements', methods=['GET', 'POST'])
def measurements():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return init()
    
import plotly.graph_objs as go
import plotly
import plotly.io as pio
import json

pio.templates["draft"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="DRAFT",
            textangle=-30,
            opacity=0.1,
            font=dict(color="black", size=10),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ]
)


def handle_post_request():
    form_data = request.form
    plotType = form_data.get('type')
    series = form_data.getlist('series')
    sat = form_data.getlist('sat')
    site = form_data.getlist('site')
    xaxis = form_data.get('key')
    yaxis = form_data.getlist('key2')
    current_app.logger.info(f"GET {plotType}, {series}, {sat}, {site}, {xaxis}, {yaxis}, {yaxis+[xaxis]}")
    current_app.logger.info("Getting Connection")
    with MongoDB(session["mongo_ip"], data_base=session["mongo_db"], port=session["mongo_port"]) as client:
        result = client.get_data("Measurements", None, site, sat, series, yaxis+[xaxis])
    if len(result) == 0:
        return render_template("measurements.jinja", content=client.mongo_content, plot_type=plotType, message="Nothing to plot")
    trace = []
    mode = "lines"
    table = {}
    for data in result:
        for _yaxis in yaxis:
            trace.append(go.Scatter(x=data[xaxis], y=data[_yaxis], mode=mode, name='TEST'))
            table[' '.join(data['_id'].values())]= {"mean": np.array(data[_yaxis]).mean() }
            print(table)
    fig = go.Figure(data=trace)
    fig.update_layout(showlegend=True)
    return render_template("measurements.jinja", content=client.mongo_content,
                            plot_type=plotType, graphJSON=pio.to_html(fig), mode="plotly", 
                            table_data= table, table_headers=['RMS', 'mean'])


def init():
    connect_db_ip = session["mongo_ip"]
    db_name = session["mongo_db"]
    db_port = session["mongo_port"]
    print(connect_db_ip, db_name)
    #TODO Later, database content, can be loaded in the session
    client = MongoDB(url=connect_db_ip, port=db_port, data_base=db_name)
    client.connect()
    client.get_content()
    return render_template("measurements.jinja", content=client.mongo_content, plot_type=plotType)
