from flask import Blueprint
from backend.routes.analyzer import analyzer_bp
from backend.routes.proportionings import proportionings_bp
from backend.routes.regressor import regressor_bp
from backend.routes.vms import vms_bp

def register_routes(app):
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(proportionings_bp)
    app.register_blueprint(regressor_bp)
    app.register_blueprint(vms_bp)
