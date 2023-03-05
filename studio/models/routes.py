from .base import MixinBase, db


class Routes(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    allow_startswith = db.Column(db.Text, nullable=False, comment="直接放行无需鉴权的URL")
    note = db.Column(db.Text, nullable=True, comment="备注")
