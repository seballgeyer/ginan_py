from flask import Blueprint, render_template, request, session
from flask import current_app
from sateda.dbconnector.mongo import MongoDB
from pymongo.errors import ServerSelectionTimeoutError

# eda_bp = Blueprint('eda', __name__)

dbconection_bp = Blueprint('dbConnector', __name__)


@dbconection_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Render the index page with the database connection form.

    This function handles both GET and POST requests. For GET requests, it simply renders the 'connect.html' template.
    For POST requests, it calls the appropriate handler based on the form data.

    Returns:
        The rendered template 'connect.html' for GET requests, or the result from the corresponding handler for POST requests.
    """
    if request.method == 'POST':
        return handle_post_request()
    else:
        db_ip = getattr(session, "mongo_ip", "127.0.0.1")
        db_port = getattr(session, "mongo_port", "27017")
        return render_template('connect.jinja', db_ip=db_ip, db_port=db_port)


def handle_post_request():
    """
    Handle the POST request from the database connection form.

    Based on the form data, this function calls the appropriate handler function.

    Returns:
        The result from the corresponding handler function.
    """
    form_data = request.form
    db_ip = getattr(session, "mongo_ip", "127.0.0.1")
    db_port = getattr(session, "mongo_port", "27017")
    if 'connect' in form_data:
        #TODO: need to raise exception (DB connection failed)
        return handle_connect_request(form_data)
    elif 'load' in form_data:
        return handle_load_request(form_data)
    else:
        # Handle other POST requests if needed
        return render_template('connect.jinja', db_ip=db_ip, db_port=db_port)


def handle_connect_request(form_data):
    """
    Handle the 'connect' request from the database connection form.

    This function connects to the specified database using the provided IP address and port.
    It retrieves the list of databases and renders the 'connect.html' template with the necessary data.

    Args:
        form_data: The form data containing the IP address and port.

    Returns:
        The rendered template 'connect.html' with the retrieved data.
    """
    connect_db_ip = form_data.get('db_ip', '')
    db_port = int(form_data.get('db_port', 27017))

    current_app.logger.info(f"connecting to {connect_db_ip}")
    try:
        client = MongoDB(url=connect_db_ip, port=db_port)
        client.connect()
        databases = client.get_list_db()
        return render_template('connect.jinja', db_ip=connect_db_ip, db_port=db_port, databases=databases)
    except ServerSelectionTimeoutError:
        error_message = f"Connection failed: MongoDB server doesn't exist or is not reachable. {connect_db_ip}:{db_port}"
        return render_template('connect.jinja', db_ip=connect_db_ip, db_port=db_port, message=error_message)



def handle_load_request(form_data):
    """
    Handle the 'load' request from the database connection form.

    This function connects to the specified database and retrieves its content.
    It stores the connection information in the session and renders the 'connect.html' template with the retrieved data.

    Args:
        form_data: The form data containing the IP address, port, and database name.

    Returns:
        The rendered template 'connect.html' with the retrieved data.
    """
    connect_db_ip = form_data.get('db_ip', '')
    db_name = form_data.get('dataset', '')
    db_port = int(form_data.get('db_port', 27017))
    current_app.logger.info(f"connection to {connect_db_ip}, {db_name}")
    client = MongoDB(connect_db_ip, data_base=db_name)
    client.connect()
    databases = client.get_list_db()
    client.get_content()
    session["mongo_ip"] = connect_db_ip
    session["mongo_db"] = db_name

    nsat = len(client.mongo_content['Sat'])
    nsite = len(client.mongo_content['Site'])
    message = f"connected to {db_name}:  has {nsat} satellites and {nsite} sites"
    # Move the selected database to the end of the list (to ensure it is selected.)
    if db_name in databases:
        databases.remove(db_name)
        databases.insert(0, db_name)

    return render_template('connect.jinja', db_ip=connect_db_ip, db_port=db_port, databases=databases, message=message)


#TODO This doesn't work yet.0
# @eda_bp.errorhandler(404)
# def page_not_found(error):
#     print("entering 404")
#     return render_template('404.html'), 404