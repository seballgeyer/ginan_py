from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB

# eda_bp = Blueprint('eda', __name__)

config_bp = Blueprint("config", __name__)


@config_bp.route("/config", methods=["GET", "POST"])
def config():
    with MongoDB(session["mongo_ip"], data_base=session["mongo_db"], port=session["mongo_port"]) as client:
        config = client.get_config()
    print(len(config))
    print(config)
    config["_id"] = str(config["_id"])
    return render_template("config.jinja", config=config)
