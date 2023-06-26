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

    db_, series_ = form["series"].split("\\")
    db_2, series_2 = form["series_base"].split("\\")
    if db_ != db_2:
        return render_template(
            "clocks.jinja",
            # content=client.mongo_content,
            extra=extra,
            message=f"Error getting data: Can only compare series from the same database",
        )
    with MongoDB(session["mongo_ip"], data_base=db_, port=session["mongo_port"]) as client:
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
                [series_] + [series_2],
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
        clocks = Clocks(data, satlist=sat_list, series=series_, series_base=series_2)
    else:
        clocks = Clocks(data, sitelist=site_list, series=series_, series_base=series_2)
    trace = []
    result = clocks.process()
    result.sort()
    result.find_minmax()
    result.adjust_slice(minutes_min=form["exclude"], minutes_max=None)
    result.get_stats()
    table={}
    for _clock in result:
        trace.append(
            go.Scatter(
                x=_clock.epoch[_clock.subset],
                y=_clock.data["x"][_clock.subset],
                mode="lines",
                name=f"{_clock.id}",
                hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>" + "%{y:.4e%}<br>" + f"{_clock.id}",
            )
        )
        print(_clock.info)
        table[f"{_clock.id}"] = {"mean": _clock.info['x']["mean"],
                            "RMS": _clock.info['x']["rms"]}
        
    table_agg = {}
    for _data in result :
        series_ = _data.id["series"]
        db_ = _data.id["db"]
        name = f" "
        if name not in table_agg:
            table_agg[name] = {"mean": 0, "RMS": 0, "len": 0, "count": 0}
            print(_data.info)
            table_agg[name]["mean"] += _data.info['x']["mean"]
            table_agg[name]["RMS"] += _data.info['x']["sumsqr"]
            table_agg[name]["len"] += _data.info['x']["len"]
            table_agg[name]["count"] += 1

    for _name, _tab in table_agg.items():
        _tab["mean"] /= _tab["count"]
        _tab["RMS"] = np.sqrt(_tab["RMS"] / _tab["len"])


    fig = go.Figure(data=trace)
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True)),
        yaxis=dict(fixedrange=False, tickformat=".3e"),
        height=600,
    )

    return render_template(
        "clocks.jinja",
        content=client.mongo_content,
        extra=extra,
        graphJSON=pio.to_html(fig),
        mode="plotly",
        selection=form,
        table_data= table, 
        table_headers=["RMS", "mean"],
        tableagg_data=table_agg,
        tableagg_headers=["RMS", "mean"],
    )
