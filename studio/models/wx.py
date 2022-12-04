from .base import MixinBase, db


class WxTokens(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(1024), nullable=False, comment="微信的access_token")
    expires = db.Column(db.Integer, nullable=False, comment="access_token的过期时间，单位为秒")


class WxResponses(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    keyWord = db.Column(db.String(40), nullable=False, comment="关键词")
    type = db.Column(db.String(20), nullable=False, comment="返回类型, 取值有text或article")
    threshold = db.Column(db.Float, nullable=False, server_default=db.text("90"), comment="匹配阈值")
    tag = db.Column(db.String(64), nullable=False, comment="回复列表中的简述")
    text = db.Column(db.String(1024), comment="文本时返回的文本内容")
    title = db.Column(db.String(1024), comment="图文时提供的标题")
    description = db.Column(db.String(1024), comment="图文时提供的描述")
    picUrl = db.Column(db.String(1024), comment="图文时提供的图片静态地址, 大图360*200, 小图200*200")
    url = db.Column(db.String(1024), comment="图文时点击后跳转的链接, 比如某个推送的地址或报名的网页")


class WxUserResponses(db.Model, MixinBase):
    # 该表暂时没有什么用处，最开始是为了进行并发处理时要用到的，但是现在看来并没有类似的需求
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(128), nullable=False, comment="用户的openid")
    responseId = db.Column(db.Integer, db.ForeignKey("wx_responses.id"), comment="给用户回复的wx_responses表中的id")


class WxAppSecret(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.String(1024), nullable=False, comment="微信平台的appid")
    secret = db.Column(db.String(1024), nullable=False, comment="微信平台的appsecret")
