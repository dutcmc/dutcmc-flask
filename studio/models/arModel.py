from .base import MixinBase, db


class ArModel(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    assetId = db.Column(db.String(64), nullable=False, unique=True, comment="模型的AssetID, 必须唯一")
    name = db.Column(db.String(64), nullable=False, comment="模型的名称")
    author = db.Column(db.String(128), comment="模型提供者")
    url = db.Column(db.Text, comment="模型对应的URL, 建议使用阿里云OSS的外链")
