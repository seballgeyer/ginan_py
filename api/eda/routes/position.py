import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Blueprint, current_app, render_template, request, session

from sateda.data.measurements import MeasurementArray
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
        return "aaaa"
    else:
        return init_page(template="position.jinja")
