import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from flask import Blueprint, current_app, render_template, request, session

from sateda.dbconnector.mongo import MongoDB
from sateda.data.measurements import MeasurementArray, Measurements
from ..utilities import init_page, extra
from . import eda_bp

# eda_bp = Blueprint('eda', __name__)

measurements_bp = Blueprint("measurements", __name__)


@eda_bp.route("/measurements", methods=["GET", "POST"])
def measurements():
    if request.method == "POST":
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
    form = {}
    form["plot"] = form_data.get("type")
    form["series"] = form_data.getlist("series")
    form["sat"] = form_data.getlist("sat")
    form["site"] = form_data.getlist("site")
    form["xaxis"] = form_data.get("xaxis")
    form["yaxis"] = form_data.getlist("yaxis")
    form["exclude"] = form_data.get("exclude")
    if form["exclude"] == "":
        form["exclude"] = 0
    else:
        form["exclude"] = int(form["exclude"])
    current_app.logger.info(
        f"GET {form['plot']}, {form['series']}, {form['sat']}, {form['site']}, {form['xaxis']}, {form['yaxis']}, {form['yaxis']+[form['xaxis']]}, exclude {form['exclude']} mintues"
    )
    current_app.logger.info("Getting Connection")
    data = MeasurementArray()
    print("------")
    for series in form["series"] :
        print(series)
        db_, series_ = series.split("\\")
        with MongoDB(session["mongo_ip"], data_base=db_, port=session["mongo_port"]) as client:
            try:
                for req in client.get_data(
                    "Measurements",
                    None,
                    form["site"],
                    form["sat"],
                    [series_],
                    form["yaxis"] + [form["xaxis"]],
                ):
                    try:
                        data.append(Measurements.from_dictionary(req))
                    except ValueError as err:
                        current_app.logger.warning(err)
                        continue   
            except ValueError as err:
                current_app.logger.warning(err)
                continue               
    if len(data.arr) == 0:
        return render_template(
            "measurements.jinja",
            content=client.mongo_content,
            extra=extra,
            message=f"Error getting data: No data",
        )
    print(data)
    data.find_minmax()
    data.adjust_slice(minutes_min=form["exclude"], minutes_max=None)
    for data_ in data:
        data_.find_gaps()
    trace = []
    mode = "markers+lines" if form["plot"] == "Scatter" else "lines"
    table = {}
    for _data in data:
        for _yaxis in form["yaxis"]:
            trace.append(
                go.Scatter(
                    x=_data.epoch[_data.subset],
                    y=_data.data[_yaxis][_data.subset],
                    mode=mode,
                    name=f"{_data.id}",
                    hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>" + "%{y:.4e%}<br>" + f"{_data.id}",
                )
            )
            table[f"{_data.id}"] = {"mean": np.array(_data.data[_yaxis][_data.subset]).mean()}
    fig = go.Figure(data=trace)
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=False)),
        yaxis=dict(fixedrange=False, tickformat=".3f"),
        height=800,
    )
    fig.layout.autosize = True
    return render_template(
        "measurements.jinja",
        content=client.mongo_content,
        extra=extra,
        graphJSON=pio.to_html(fig),
        mode="plotly",
        selection=form,
        table_data=table,
        table_headers=["RMS", "mean"],
    )
