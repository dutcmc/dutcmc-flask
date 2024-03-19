from flask import Blueprint, request
import requests
import json
from studio.models import WxgetWerunData

werun = Blueprint("werun", __name__, url_prefix="/werun")

import base64
import json
from Crypto.Cipher import AES

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

@werun.route('hello')
def hello():
    return "hello world!"
@werun.route("/login", methods=["GET", "POST"])
def login():
    data = request.json
    code = data["code"]
    appID = 'wxbd72b81f421cef8d'  # 开发者关于微信小程序的appID
    appSecret = 'a0c98e149f997763a7d08b9d74640a5e'  # 开发者关于微信小程序的appSecret
    global openid, session_key
    req_params = {
        'appid': appID,
        'secret': appSecret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    wx_login_api = 'https://api.weixin.qq.com/sns/jscode2session'
    response_data = requests.get(wx_login_api, params=req_params)  # 向API发起GET请求
    resData = response_data.json()
    openid = resData['openid']  # 得到用户关于当前小程序的OpenID
    session_key = resData['session_key']  # 得到用户关于当前小程序的会话密钥session_key
    reply = "code:" + code + "  openid:" + openid + " session_key:" + session_key
    print(reply)
    return reply

@werun.route('/encrydata', methods=["GET","POST"])
def encrydata():
    data = request.json
    unencryeddata = data["unencryeddata"]
    iv = data["iv"]

    pc = WXBizDataCrypt('wxbd72b81f421cef8d', session_key)

    stepdata = pc.decrypt(unencryeddata, iv)
    step = stepdata['stepInfoList'][-1]['step']
    print(step)
    return json.dumps(step)

