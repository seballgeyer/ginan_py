import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Blueprint, current_app, render_template, request, session

from sateda.dbconnector.mongo import MongoDB

from ..utilities import init_page, extra

states_bp = Blueprint("states", __name__)

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

# @states_bp.route('/states', methods=['GET', 'POST'])
# def states() -> str:
#     """
#     Overall handeling of the page.

#     :return str: HTML code
#     """
#     print(request)
#     if request.method == 'POST':
#         current_app.logger.info("Entering request")
#         return handle_post_request()
#     else:
#         return init_page(template="states.jinja")


@states_bp.route("/states", methods=["GET", "POST"])
def states():
    if request.method == "POST":
        return handle_post_request()
    else:
        return init_page(template="states.jinja")


def handle_post_request() -> str:
    """
    handle_post_request Code to process the POST request and generate the HTML code

    :return str: webpage code
    """
    current_app.logger.info("Entering request")
    form_data = request.form
    form = {}
    form["plot"] = form_data.get("type")
    form["series"] = form_data.getlist("series")
    form["sat"] = form_data.getlist("sat")
    form["site"] = form_data.getlist("site")
    form["state"] = form_data.getlist("state")
    form["xaxis"] = "Epoch"
    form["yaxis"] = form_data.getlist("yaxis")
    form["exclude"] = form_data.get("exclude")
    form["process"] = form_data.get("process")
    form["degree"] = form_data.get("degree")
    if form["exclude"] == "":
        form["exclude"] = 0
    else:
        form["exclude"] = int(form["exclude"])

    print(form["process"], form["degree"])
    current_app.logger.info(
        f"GET {form['plot']}, {form['series']}, {form['sat']}, {form['site']}, {form['state']}, {form['xaxis']}, {form['yaxis']}, "
        f"{form['yaxis']+[form['xaxis']]}, exclude {form['exclude']} mintues"
    )
    with MongoDB(session["mongo_ip"], data_base=session["mongo_db"], port=session["mongo_port"]) as client:
        try:
            data = client.get_data_to_measurement(
                "States",
                form["state"],
                form["site"],
                form["sat"],
                form["series"],
                form["yaxis"] + [form["xaxis"]],
            )
        except Exception as err:
            current_app.logger.error(err)
            return render_template(
                "states.jinja",
                content=client.mongo_content,
                extra=extra,
                message=f"Error getting data: {str(err)}",
            )
    print(len(data.arr))
    data.find_minmax()
    data.adjust_slice(minutes_min=form["exclude"], minutes_max=None)
    trace = []
    mode = "lines"
    table = {}
    if form["process"] == "Detrend":
        for _data in data:
            _data.detrend(degree=int(form["degree"]))

    for _data in data:
        for _yaxis in form["yaxis"]:
            for i in range(_data.data[_yaxis].shape[1]):
                _data.id["state"] = _yaxis
                _data.id["ax"] = i
                trace.append(
                    go.Scatter(
                        x=_data.epoch[_data.subset],
                        y=_data.data[_yaxis][_data.subset, i],
                        mode=mode,
                        name=f"{_data.id}",
                        hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>" + "%{y:.4e%}<br>" + f"{_data.id}",
                    )
                )
                table[f"{_data.id}"] = {"mean": np.array(_data.data[_yaxis][i][_data.subset]).mean()}
    fig = go.Figure(data=trace)
    fig.update_layout(showlegend=True)
    return render_template(
        "states.jinja",
        content=client.mongo_content,
        extra=extra,
        graphJSON=pio.to_html(fig),
        mode="plotly",
        selection=form,
        table_data=table,
        table_headers=["RMS", "mean"],
    )
