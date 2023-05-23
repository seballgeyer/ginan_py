from .dbConnection import dbconection_bp


def register_routes(app):
    app.register_blueprint(dbconection_bp)