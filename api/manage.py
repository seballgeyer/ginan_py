import json

from eda.routes import register_routes
from flask import Flask

app = Flask(__name__, template_folder='templates')
app.secret_key = "secret"

def dict_filter(value):
    return json.dumps(value)

# Make the 'dict' filter available in the Jinja environment
app.jinja_env.filters['dict'] = dict_filter

register_routes(app)


@app.template_filter('to_dict')
def to_dict_filter(value):
    return dict(value)



if __name__ == '__main__':
    app.run()