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


@secret.route("/upsertSecret", methods=["POST"])
def r_upsert_secret():
    dictData = request.get_json()["secret"]
    appid = dictData["appid"]
    appSecret = dictData["secret"]
    querySecret = db.session.query(WxAppSecret).filter(WxAppSecret.appid == appid).first()
    if querySecret is None:
        # appid 不存在
        wxAppSecret = WxAppSecret(appid=appid, secret=appSecret)
        db.session.add(wxAppSecret)
        db.session.commit()
    else:
        querySecret.secret = appSecret
        db.session.add(querySecret)
        db.session.commit()

    return {"success": True}

