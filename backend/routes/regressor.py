from flask import Blueprint, render_template

regressor_bp = Blueprint('regressor', __name__)

@regressor_bp.route("/regressor")
def regressor():
    return render_template("Regressor.html")
