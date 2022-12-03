import hashlib
import os
import time

from flask import Blueprint, request
from studio.utils import wx, dfl
from studio.models import WxResponses, WxUserResponses, db

jizhetuan = Blueprint("jizhetuan", __name__, url_prefix="/jizhetuan")

appid = os.getenv("JIZHETUAN_WX_APPID")
secret = os.getenv("JIZHETUAN_WX_SECRET")
wx_token = os.getenv("JIZHETUAN_WX_TOKEN")


@jizhetuan.route("/hello", methods=["POST", "GET"])
def r_hello():
    if request.method == "GET":
        signature = request.args.get("signature", "")
        timestamp = request.args.get("timestamp", "")
        nonce = request.args.get("nonce", "")
        echostr = request.args.get("echostr", "")
        if echostr:
            # 如果有 echostr 就是进行服务器校验，否则就是正常的get
            # 进行字典排序
            global wx_token
            data = [wx_token, timestamp, nonce]
            data.sort()
            # 三个参数拼接成一个字符串并进行sha1加密
            temp = "".join(data)
            sha1 = hashlib.sha1(temp.encode("utf-8"))
            hashcode = sha1.hexdigest()
            # 对比获取到的signature与根据上面token生成的hashcode，如果一致，则返回echostr，对接成功
            if hashcode == signature:
                return echostr
            else:
                return "error"
        else:
            # 相应正常的请求
            pass
    if request.method == "POST":
        # 处理 POST 请求，主要是用户向后台发送的信息
        # < xml >
        # < ToUserName > <![CDATA[toUser]] > < / ToUserName >
        # < FromUserName > <![CDATA[fromUser]] > < / FromUserName >
        # < CreateTime > 1348831860 < / CreateTime >
        # < MsgType > <![CDATA[text]] > < / MsgType >
        # < Content > <![CDATA[this is a test]] > < / Content >
        # < MsgId > 1234567890123456 < / MsgId >
        # < MsgDataId > xxxx < / MsgDataId >
        # < Idx > xxxx < / Idx >
        # < / xml >
        xmlContent = request.data
        msgType = wx.get_xml_data(xmlContent, "MsgType")
        toUserName = wx.get_xml_data(xmlContent, "ToUserName")  # 开发者微信号
        fromUserName = wx.get_xml_data(xmlContent, "FromUserName")  # 用户的openId
        print("msgType:", msgType)
        if msgType == "text":
            return wx.handle_text_response(xmlContent)
        else:
            return wx.handle_invalid_response(xmlContent)
        # return wx.generate_text_response(fromUserName, toUserName, time.time(), "回复功能正在升级中~敬请期待~！")


@jizhetuan.route("/createResponse", methods=["POST"])
def r_add_response():
    response = request.get_json()["response"]
    wxResponse = WxResponses(**dfl(response, ["keyWord", "type", "threshold","tag", "text", "title", "description",
                                              "picUrl", "url"]))
    db.session.add(wxResponse)
    db.session.commit()
    return {"success": True}


@jizhetuan.route("/setResponse", methods=["POST"])
def r_edit_response():
    response = request.get_json()["response"]
    wxResponse = WxResponses.query.get(response["id"])
    wxResponse.keyWord = response["keyWord"]
    wxResponse.type = response["type"]
    wxResponse.tag = response["tag"]
    wxResponse.threshold = response["threshold"]
    wxResponse.text = response["text"]
    wxResponse.title = response["title"]
    wxResponse.description = response["description"]
    wxResponse.picUrl = response["picUrl"]
    wxResponse.url = response["url"]
    db.session.commit()
    return {"success": True}


@jizhetuan.route("/getResponses", methods=["GET"])
def r_get_responses():
    responses = WxResponses.query.filter(WxResponses.deleted == 0).all()
    result = []
    for response in responses:
        result.append(wx.generate_response_query_dict(response))
    return result


@jizhetuan.route("/getDeletedResponses", methods=["GET"])
def r_get_deleted_responses():
    responses = WxResponses.query.filter(WxResponses.deleted == 1).all()
    result = []
    for response in responses:
        result.append(wx.generate_response_query_dict(response))
    return result


@jizhetuan.route("/deleteResponse", methods=["POST"])
def r_delete_response():
    response = request.get_json()["response"]
    wxResponse = WxResponses.query.get(response["id"])
    wxResponse.deleted = 1
    db.session.commit()
    return {"success": True}


@jizhetuan.route("/recoverResponse", methods=["POST"])
def r_recover_response():
    response = request.get_json()["response"]
    wxResponse = WxResponses.query.get(response["id"])
    wxResponse.deleted = 0
    db.session.commit()
    return {"success": True}


