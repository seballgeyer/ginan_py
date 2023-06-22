import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Blueprint, current_app, render_template, request, session

from sateda.data.measurements import MeasurementArray
from sateda.data.position import Position
from sateda.dbconnector.mongo import MongoDB

from ..utilities import init_page, extra
from . import eda_bp

# eda_bp = Blueprint('eda', __name__)


@eda_bp.route("/position", methods=["GET", "POST"])
def position() -> str:
    """
    Overall handeling of the page.

    :return str: HTML code
    """
    if request.method == "POST":
        return handle_post_request()
    else:
        return init_page(template="position.jinja")

def handle_post_request() -> str:
    current_app.logger.info("Entering request")
    form_data = request.form
    form = {}
    form["type"] = form_data.get("type")
    form["series"] = form_data.get("series")
    form["series_base"] = form_data.get("series_base")
    form["exclude"] = form_data.get("exclude")
    if form["exclude"] == "":
        form["exclude"] = 0
    else:
        form["exclude"] = int(form["exclude"])
    form["mode"] = form_data.get("mode")
    form["site"] = form_data.getlist("site")
    print(form["mode"], form["site"], form["series"], form["series_base"])
    db_, series_ = form["series"].split("\\")
    db_2, series_2 = form["series_base"].split("\\")
    if db_ != db_2:
        return render_template(
            "position.jinja",
            # content=client.mongo_content,
            extra=extra,
            message=f"Error getting data: Can only compare series from the same database",
        )
        
    with MongoDB(session["mongo_ip"], data_base=db_, port=session["mongo_port"]) as client:
        try:
            data = client.get_data_to_measurement(
                "States",
                ["REC_POS"],
                form["site"],
                [""],
                [series_] ,
                ["x"],
            )
            base = client.get_data_to_measurement(
                "States",
                ["REC_POS"],
                form["site"],
                [""],
                [series_2] ,
                ["x"],
            )
        except Exception as err:
            current_app.logger.error(err)
            return render_template(
                "position.jinja",
                content=client.mongo_content,
                extra=extra,
                message=f"Error getting data: {str(err)}",
            )
    # print(len(data.arr),len(base.arr))
    position = Position(data, base)
    if form["mode"] == "ENU":
        position.rotate_enu()
    print("..., ", form["exclude"])
    position.data.find_minmax()
    print(position.data.tmin, position.data.tmax)
    position.data.adjust_slice(minutes_min=form["exclude"], minutes_max=None)
    # residuals = data - base
    trace = []
    table = {}
    type = "markers+lines" if form["type"] == "Scatter" else "lines"
    for _data in position:
        print(_data.data["x"].shape)
        for i in range(3):
            trace.append(
                go.Scatter(
                    x=_data.epoch[_data.subset],
                    y=_data.data["x"][_data.subset,i],
                    mode=type,
                    name=f"{_data.id}{i}",
                    hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>" + "%{y:.4e%}<br>" + f"{_data.id}{i}",
                )
            )
            table[f"{_data.id}_{i}"] = {"mean": np.nanmean(_data.data["x"][_data.subset,i]),
                        "RMS": np.sqrt(np.nanmean(_data.data["x"][_data.subset,i]**2))}   
    fig = go.Figure(data=trace)
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True)),
        yaxis=dict(fixedrange=False),
        height=600,
    )

    return render_template(
        "position.jinja",
        content=client.mongo_content,
        extra=extra,
        graphJSON=pio.to_html(fig),
        mode="plotly",
        selection=form,
        table_data= table, 
        table_headers=["RMS", "mean"],
    )