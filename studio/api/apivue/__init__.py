from flask import Blueprint, current_app, request
from flask_cors import CORS
from studio.models import db, Users, UserGroups
from studio.utils import dfl, listf, abort_err
from studio.utils.jwt import create_token

from .enroll import enroll

apivue = Blueprint("apivue", __name__, url_prefix="/apivue")
apivue.register_blueprint(enroll)


@apivue.route("/login", methods=["POST"])
def r_login():
    userData = request.get_json()["user"]
    print(userData)
    user = Users.query.filter(Users.username == userData["username"]).one_or_none()
    if user is None:
        return abort_err(462, "用户名不存在")
    if not user.check_password(userData["password"]):
        return abort_err(462, "密码错误")

    strToken = create_token({"id": user.id})
    return {"success": True, "details": "登录成功", "token": strToken}


@apivue.route("/register")
def r_register():
    userData = request.get_json()["user"]
    user = Users(**dfl(userData, ["username", "password"]))
    db.session.add(user)
    db.session.commit()
    return {"success": True}
