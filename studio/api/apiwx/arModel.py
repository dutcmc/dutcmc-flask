from flask import Blueprint, request
from studio.utils import dfln
from studio.models import db, ArModel

arModel = Blueprint("arModel", __name__, url_prefix="/arModel")


@arModel.route("/getModelArray", methods=["GET"])
def r_get_model_array():
    models = ArModel.query.all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in models]
    return {"models": result}


@arModel.route("/getAppInfo", methods=["GET"])
def r_get_app_info():

    return {"info": ""}