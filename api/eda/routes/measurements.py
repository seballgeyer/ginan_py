from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB

# eda_bp = Blueprint('eda', __name__)

measurements_bp = Blueprint('measurements', __name__)


@measurements_bp.route('/measurements', methods=['GET', 'POST'])
def measurements():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return init()
    
def handle_post_request():
    return "aaaa"

def init():
    connect_db_ip = session["mongo_ip"]
    db_name = session["mongo_db"]
    print(connect_db_ip, db_name)
    client = MongoDB(url=connect_db_ip, data_base=db_name)
    client.connect()
    client.get_content()
    return render_template("measurements.jinja", content=client.mongo_content)
