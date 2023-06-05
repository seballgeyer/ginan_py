from .dbConnection import dbconection_bp
from .measurements import measurements_bp
from .config import config_bp
from .states import states_bp
from .errorPages import error_bp
from .position import position_bp

def register_routes(app):
    app.register_blueprint(dbconection_bp)
    app.register_blueprint(measurements_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(states_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(position_bp)