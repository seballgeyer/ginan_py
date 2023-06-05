import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from flask import Blueprint, current_app, render_template, request, session

from sateda.data.measurements import MeasurementArray, Measurements
from sateda.dbconnector.mongo import MongoDB

from ..utilities import init_page, plotType
# eda_bp = Blueprint('eda', __name__)

measurements_bp = Blueprint('measurements', __name__)

@measurements_bp.route('/measurements', methods=['GET', 'POST'])
def measurements():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return init_page(template="measurements.jinja")


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
    plot = form_data.get('type')
    series = form_data.getlist('series')
    sat = form_data.getlist('sat')
    site = form_data.getlist('site')
    xaxis = form_data.get('key')
    yaxis = form_data.getlist('key2')
    exclude = form_data.get('exclude')
    if exclude == "":
        exclude = 0
    else:
        exclude = int(exclude)
    current_app.logger.info(f"GET {plot}, {series}, {sat}, {site}, {xaxis}, {yaxis}, {yaxis+[xaxis]}, exclude {exclude} mintues")
    current_app.logger.info("Getting Connection")
    with MongoDB(session["mongo_ip"], data_base=session["mongo_db"], port=session["mongo_port"]) as client:
        try:
            data = client.get_data_to_measurement("Measurements", None, site, sat, series, yaxis+[xaxis])
        except Exception as err:
            current_app.logger.error(err)
            return render_template("measurements.jinja", content=client.mongo_content, plot_type=plotType, message=f"Error getting data: {str(err)}")
    data.find_minmax()
    data.adjust_slice(minutes_min=exclude, minutes_max=None)
    trace = []
    mode = "lines"
    table = {}
    for _data in data:
        for _yaxis in yaxis:
            trace.append(go.Scatter(x=_data.epoch[_data.subset], y=_data.data[_yaxis][_data.subset], mode=mode, name=f"{_data.id}",
                                    hovertemplate = "%{x|%Y-%m-%d %H:%M:%S}<br>" +
                                                    "%{y:.4e%}<br>" +
                                                    f"{_data.id}"
                                    ))
            table[f"{_data.id}"]= {"mean": np.array(_data.data[_yaxis][_data.subset]).mean() }
    fig = go.Figure(data=trace)
    fig.update_layout(showlegend=True)
    return render_template("measurements.jinja", content=client.mongo_content,
                            plot_type=plotType, graphJSON=pio.to_html(fig), mode="plotly", 
                            table_data= table, table_headers=['RMS', 'mean'])

