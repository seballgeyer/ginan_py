from flask import Flask
from eda.routes import eda_bp


app = Flask(__name__, template_folder='templates')
app.register_blueprint(eda_bp, url_prefix='/eda')


if __name__ == '__main__':
    app.run()