from .dbConnection import dbconection_bp
from .measurements import measurements_bp


def register_routes(app):
    app.register_blueprint(dbconection_bp)
    app.register_blueprint(measurements_bp)