import hashlib
import os
import time

from flask import Blueprint, request
from studio.models import WxAppSecret, db

secret = Blueprint("secret", __name__, url_prefix="/secret")


@secret.route("/getSecret", methods=["POST"])
def r_get_secret():
    appid = request.get_json()["appid"]
    querySecret = db.session.query(WxAppSecret).filter(WxAppSecret.appid == appid).first()
    if querySecret is not None:
        return {"success": True, "secret": querySecret.secret}
    else:
        return {"success": False}
