from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MixinBase:
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), comment="创建时间")
    update_time = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now(), comment="更新时间"
    )
    update_cnt = db.Column(db.SmallInteger, nullable=False, server_default=db.text("1"), comment="更新次数")
    deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("0"), comment="删除标记")
