import os
import requests
import datetime
import time
import lxml.etree as et
from studio.models import db, WxTokens, WxResponses, WxUserResponses
from fuzzywuzzy import fuzz

wx_token = os.getenv("WX_TOKEN")


def get_wx_access_token(appid, secret):
    print(appid)
    print(secret)
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    wxToken = WxTokens.query.filter(WxTokens.appid == appid).first()
    if wxToken is not None:
        print("access_token 已经存在")
        cur_time = datetime.datetime.utcnow().timestamp() + 28800.0
        update_time = wxToken.update_time.timestamp()
        expires = wxToken.expires
        print("current:"+str(cur_time))
        print("update:"+str(update_time))
        print("expires:"+str(expires))
        if cur_time - update_time > expires:
            res = requests.get(url).json()
            print("access_token 已经过期")
            if res.get("access_token"):
                # 确保 access_token 不为空
                wxToken.access_token = res.get("access_token")
                wxToken.expires = res.get("expires_in")
                db.session.add(wxToken)
                db.session.commit()
                print("access_token 已经更新")
                return res.get("access_token")
            else:
                return ""
        else:
            print("access_token 尚未过期")
            return wxToken.access_token
    else:
        print("access_token 不存在")
        res = requests.get(url).json()
        print(res)
        if res.get("access_token"):
            # 确保 access_token 不为空
            access_token = res.get("access_token")
            expires = res.get("expires_in")
            wxToken = WxTokens(appid=appid, access_token=access_token, expires=expires)
            db.session.add(wxToken)
            db.session.commit()
            return res.get("access_token")
        else:
            return ""


def generate_text_response(ToUserName, FromUserName, CreateTime, Content):
    return f"""
    <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
    </xml>
    """


def generate_music_response(ToUserName, FromUserName, CreateTime, Title, Description, MusicUrl, HQMusicUrl,
                            ThumbMediaId):
    return f"""
    <xml>
        <ToUserName><![CDATA[f{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[f{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[music]]></MsgType>
        <Music>
            <Title><![CDATA[{Title}]]></Title>
            <Description><![CDATA[{Description}]]></Description>
            <MusicUrl><![CDATA[{MusicUrl}]]></MusicUrl>
            <HQMusicUrl><![CDATA[{HQMusicUrl}]]></HQMusicUrl>
            <ThumbMediaId><![CDATA[{ThumbMediaId}]]></ThumbMediaId>
        </Music>
    </xml>
    """


# 回复多条图文消息, 但是目前会有问题
def generate_news_responses(ToUserName, FromUserName, CreateTime, ArticleCount,
                            Title: [], Description: [], PicUrl: [], Url: []):
    items = ""
    for i in range(ArticleCount):
        title = Title[i]
        description = Description[i]
        picUrl = PicUrl[i]
        url = Url[i]
        item = f"""
        <item>
            <Title><![CDATA[{title}]]></Title>
            <Description><![CDATA[{description}]]></Description>
            <PicUrl><![CDATA[{picUrl}]]></PicUrl>
            <Url><![CDATA[{url}]]></Url>
        </item> 
        """
        items += item
    return f"""
    <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>{ArticleCount}</ArticleCount>
        <Articles>
            {items}
        </Articles>
    </xml>
    """.replace("\n", "")


# 回复一条图文消息
def generate_news_response(ToUserName, FromUserName, CreateTime,
                           Title, Description, PicUrl, Url):
    return f"""
        <xml>
            <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
            <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
            <CreateTime>{CreateTime}</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>1</ArticleCount>
            <Articles>
                <item>
                    <Title><![CDATA[{Title}]]></Title>
                    <Description><![CDATA[{Description}]]></Description>
                    <PicUrl><![CDATA[{PicUrl}]]></PicUrl>
                    <Url><![CDATA[{Url}]]></Url>
                </item> 
            </Articles>
        </xml>
        """.replace("\n", "")


def generate_image_response(ToUserName, FromUserName, CreateTime, MediaId):
    return f"""
    <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
            <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
    </xml>
    """


def get_xml_data(xmlContent, tagName):
    """
    :param xmlContent: xml字符串
    :param tagName: 标签名
    :return: 返回一个读取的结果，如果失败则为None
    """
    doc = et.fromstring(xmlContent)
    content = doc.find(tagName)
    return content.text


def handle_text_response(xmlContent):
    # 考虑到并发的情况，因此必须要为不同的用户设置不同的回复列表，先判断某个用户对应的回复列表是否存在
    # wxUserResponse = WxUserResponses.query.filter(
    # WxUserResponses.openid == openId, WxUserResponses.deleted == 0).first()

    toUserName = get_xml_data(xmlContent, "ToUserName")  # 开发者微信号
    fromUserName = get_xml_data(xmlContent, "FromUserName")  # 用户的openId
    createTime = get_xml_data(xmlContent, "CreateTime")
    content = get_xml_data(xmlContent, "Content")
    msgId = get_xml_data(xmlContent, "MsgId")
    if not content.isdigit():
        #  如果不是数字，则进行查询
        responses = query_responses(content)
        if len(responses) == 0:
            # 如果id查询为空
            return generate_text_response(fromUserName, toUserName, time.time(),
                                          "好像没有相关信息呢！输入其他信息试试吧！")
        responses_text = ""
        # 做一个优化, 如果只匹配到 1 个, 就直接返回查询结果
        if len(responses) == 1:
            return send_response(xmlContent, responses[0])
        for response in responses:
            responses_text += f"{response.id} - {response.tag} \n"
        responses_text = f"""已经匹配到的回复如下~请回复序号以查看哦！\n{responses_text}"""
        return generate_text_response(fromUserName, toUserName, time.time(), responses_text)

    # 如果是数字，则直接进行回复
    wxResponse: WxResponses = WxResponses.query.filter(WxResponses.id == int(content), WxResponses.deleted == 0) \
        .one_or_none()
    return send_response(xmlContent, wxResponse)


def send_response(xmlContent, wxResponse):
    toUserName = get_xml_data(xmlContent, "ToUserName")  # 开发者微信号
    fromUserName = get_xml_data(xmlContent, "FromUserName")  # 用户的openId

    # 先对回复消息的类型进行判断
    if wxResponse is None:
        return generate_text_response(fromUserName, toUserName, time.time(), "好像没有相关的信息呢！输入其他信息试试吧！")
    # 如果找到记录再进行判断，避免 wxResponse 报 NoneType
    if wxResponse.type == "text":
        return generate_text_response(fromUserName, toUserName, time.time(), wxResponse.text)
    elif wxResponse.type == "image":
        return generate_text_response(fromUserName, toUserName, time.time(), "暂时不支持纯图片回复！")
    elif wxResponse.type == "news":
        # Articles 参数暂时处于缺省状态，注意！对于用户发送的文本信息，微信后台只能回复一则图文消息
        return generate_news_response(fromUserName, toUserName, time.time(), wxResponse.title,
                                      wxResponse.description, wxResponse.picUrl, wxResponse.url)
    else:
        return generate_text_response(fromUserName, toUserName, time.time(), "好像没有相关的信息呢！输入其他信息试试吧！")


def handle_invalid_response(xmlContent):
    toUserName = get_xml_data(xmlContent, "ToUserName")  # 开发者微信号
    fromUserName = get_xml_data(xmlContent, "FromUserName")  # 用户的openId
    return generate_text_response(fromUserName, toUserName, time.time(), "暂时不支持回复这类消息呢！输入其他消息试试吧！")


def query_responses(keyWord):
    responses = WxResponses.query.all()
    matchedResponses = []
    for response in responses:
        t = fuzz.partial_ratio(keyWord, response.keyWord)
        threshold = response.threshold
        if t >= threshold:
            matchedResponses.append(response)
    return matchedResponses


def generate_response_query_dict(response: WxResponses):
    return {
        "id": response.id,
        "keyWord": response.keyWord,
        "type": response.type,
        "threshold": response.threshold,
        "text": response.text,
        "tag": response.tag,
        "title": response.title,
        "description": response.description,
        "picUrl": response.picUrl,
        "url": response.url
    }
