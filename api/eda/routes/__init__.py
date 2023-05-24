from .dbConnection import dbconection_bp
from .measurements import measurements_bp
from .config import config_bp

def register_routes(app):
    app.register_blueprint(dbconection_bp)
    app.register_blueprint(measurements_bp)
    app.register_blueprint(config_bp)