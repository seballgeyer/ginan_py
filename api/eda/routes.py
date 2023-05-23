from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB

eda_bp = Blueprint('eda', __name__)



@eda_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Render the index page with the form to connect to a database.

    This function handles both GET and POST requests. If a POST request is made, it retrieves the 'db_ip' value from the form, connects to the specified database,
    and fetches the list of databases. The retrieved data is then passed to the 'connect.html' template for rendering.

    Returns:
        The rendered template 'connect.html' with the required data.
    """
    #TODO: username, password not implementated yet.
    connect_db_ip = ""
    databases = []
    db_port = 27017
    db_username = ""
    db_password = ""
    db_name = ""
    message = ""
    if request.method == "POST":
        print(request.form)
        if "connect" in request.form:
            connect_db_ip = request.form['db_ip']
            db_port = int(request.form['db_port'])
            current_app.logger.info(f"connecting to {connect_db_ip}")
            client = MongoDB(url=connect_db_ip, port=db_port)
            client.connect()
            databases = client.get_list_db()
            print(databases)
        if "load" in request.form:
            connect_db_ip = request.form['db_ip']
            db_name = request.form['dataset']
            current_app.logger.info(f"connection to {connect_db_ip} , {db_name}")
            client = MongoDB(connect_db_ip, data_base= db_name)
            client.connect()
            databases = client.get_list_db()
            client.get_content()
            session["client"] = client
            nsat = len(client.mongo_content['Sat'])
            nsite = len(client.mongo_content['Site'])
            message = f"connect to {db_name} \n has {nsat} satellites and {nsite} sites"
    return render_template('connect.html', db_ip=connect_db_ip, db_port= db_port, db_username = db_username, db_password=db_password ,databases=databases, message=message)


@eda_bp.route('/hello')
def hello():
    return render_template("base.html")

#TODO This doesn't work yet.0
# @eda_bp.errorhandler(404)
# def page_not_found(error):
#     print("entering 404")
#     return render_template('404.html'), 404