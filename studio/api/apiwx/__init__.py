import base64
import requests

from flask import Blueprint, request

from studio.utils import wx
from studio.models import WxAppSecret, db
from .jizhetuan import jizhetuan

apiwx = Blueprint("apiwx", __name__, url_prefix="/apiwx")
apiwx.register_blueprint(jizhetuan)


@apiwx.route("/getAccessToken", methods=["POST"])
def r_get_access_token():
    data = request.get_json()
    appid = data.get("appid")
    secret = db.session.query(WxAppSecret).filter(WxAppSecret.appid == appid).first().secret

    if appid is None or secret is None:
        return {"success": False, "detail": "参数不足"}

    token = wx.get_wx_access_token(appid, secret)
    if token == "":
        return {"success": False, "detail": "请求 access_token 失败"}
    else:
        return {"success": True, "token": token}


@apiwx.route("/imgSecCheck", methods=["POST"])
def r_img_sec_check():
    data = request.get_json()
    token = data.get("access_token")
    base64img = data.get("img")
    imgData = base64.b64decode(base64img)
    r = requests.post(f"https://api.weixin.qq.com/wxa/img_sec_check?access_token={token}",
                      files={"media": imgData})
    return r.json()

