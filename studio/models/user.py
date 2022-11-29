from werkzeug.security import check_password_hash, generate_password_hash

from .base import MixinBase, db


class Users(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, comment="用户名")
    password_hash = db.Column(db.String(150), nullable=False, comment="密码Hash")
    last_login_ip = db.Column(db.String(50), nullable=True, comment="最后登录IP")
    last_login_time = db.Column(db.DateTime, nullable=True, comment="最后登录时间")
    # group_id = db.Column(db.Integer, db.ForeignKey("user_groups.id"))

    @property
    def password(self):
        raise AttributeError("明文密码不可读")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserGroups(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(20), nullable=False, comment="用户组名")
    description = db.Column(db.Text, nullable=True, comment="说明")

