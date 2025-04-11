from flask import Blueprint, render_template

vms_bp = Blueprint('vms', __name__)

@vms_bp.route("/vms")
def vms():
    return render_template("VMS.html")
