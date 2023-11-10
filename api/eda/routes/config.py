from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB
from . import eda_bp
from ..utilities import init_page, extra

# eda_bp = Blueprint('eda', __name__)

# config_bp = Blueprint("config", __name__)


@eda_bp.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        return handle_post_request()
    else:
        return init_page(template="config.jinja")


def handle_post_request():
    form = request.form
    database = form.get("database")
    print(database)
    with MongoDB(session["mongo_ip"], data_base=database, port=session["mongo_port"]) as client:
        configuration = client.get_config()
    configuration.pop("_id")
    return render_template("config.jinja", configuration=configuration, selection=form)
