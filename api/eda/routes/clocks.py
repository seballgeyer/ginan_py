import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Blueprint, current_app, render_template, request, session

from sateda.dbconnector.mongo import MongoDB
from sateda.data.clocks import Clocks
from ..utilities import init_page, extra
from . import eda_bp
# clocks_bp = Blueprint("clocks", __name__)


@eda_bp.route("/clocks", methods=["GET", "POST"])
def clocks():
    if request.method == "POST":
        return handle_post_request()
    else:
        return init_page(template="clocks.jinja")


def handle_post_request():
    current_app.logger.info("Entering request")
    form_data = request.form
    form = {}
    form["series"] = form_data.get("series")
    form["series_base"] = form_data.get("series_base")
    form["exclude"] = form_data.get("exclude")
    if form["exclude"] == "":
        form["exclude"] = 0
    else:
        form["exclude"] = int(form["exclude"])
    form["clockType"] = form_data.get("clockType")
    
    with MongoDB(session["mongo_ip"], data_base=session["mongo_db"], port=session["mongo_port"]) as client:
        try:
            sat_list = client.mongo_content["Sat"]
            site_list = client.mongo_content["Site"]
            if form["clockType"] == "Satellite":
                state = ["SAT_CLOCK"]
                site_list = [""]
            elif form["clockType"] == "Site":
                state = ["REC_CLOCK"]
                sat_list = ["", "G--"]
            data = client.get_data_to_measurement(
                "States",
                state,
                site_list,
                sat_list,
                [form["series"]] + [form["series_base"]],
                ["x"],
            )
        except Exception as err:
            current_app.logger.error(err)
            return render_template(
                "clocks.jinja",
                content=client.mongo_content,
                extra=extra,
                message=f"Error getting data: {str(err)}",
            )
    if form["clockType"] == "Satellite":
        clocks = Clocks(data, satlist=sat_list, series=form["series"], series_base=form["series_base"])
    else:
        clocks = Clocks(data, sitelist=site_list, series=form["series"], series_base=form["series_base"])
    trace = []
    for _clock in clocks.process():
        trace.append(
            go.Scatter(
                x=_clock.epoch,
                y=_clock.data["x"],
                mode="lines",
                name=f"{_clock.id}",
                hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>" + "%{y:.4e%}<br>" + f"{_clock.id}",
            )
        )
        # table[f"{_data.id}"]= {"mean": np.array(_data.data[_yaxis][i][_data.subset]).mean() }
    fig = go.Figure(data=trace)
    fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True)),
            yaxis=dict(fixedrange=False),
            height=600,
        )

    return render_template(
        "clocks.jinja",
        content=client.mongo_content,
        extra=extra,
        graphJSON=pio.to_html(fig),
        mode="plotly",
        selection=form,
        # table_data= table, t
        able_headers=["RMS", "mean"],
    )
