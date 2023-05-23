from flask import Flask
from eda.routes import register_routes


app = Flask(__name__, template_folder='templates')
app.secret_key = "secret"
register_routes(app)


if __name__ == '__main__':
    app.run()