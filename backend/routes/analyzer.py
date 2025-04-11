from flask import Blueprint, render_template

analyzer_bp = Blueprint('analyzer', __name__)

@analyzer_bp.route("/analyzer")
def analyzer():
    return render_template("Analyzer.html")
