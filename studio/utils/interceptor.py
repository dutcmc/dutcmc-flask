from flask import current_app, g, request
from studio.models import Users, db
from studio.utils import abort_err, cache
from studio.utils.jwt import load_token


def global_interceptor():
    # 对于放行类的接口，可以都存储到一个数据表里，这里因为记录少，就不再存了
    allow_startswith = [
        "/apiwx/jizhetuan/hello",  # 微信开放接口
        "/apiwx/getAccessToken",  # 请求 access_token
        "/apiwx/imgSecCheck",
        "/apiwx/avatar",
        "/apivue/enroll/getDepts",  # 报名接口
        "/apivue/enroll/getTurns",  # 报名接口
        "/apivue/enroll/submit",  # 报名接口
        "/apivue/enroll/verifyUnique",
        "/apivue/login"
    ]
    for startswith in allow_startswith:
        if request.path.startswith(startswith):
            return None
    # 直接放行 OPTIONS
    if request.method == "OPTIONS":
        return None

    # 其余接口都需要进行 token 验证
    payload = load_token(request.headers.get("auth"))
    if payload == "ExpiredSignature":
        return abort_err(463, login_target=request.path)

    if payload is None:
        # 发生了 token 认证失败或者是非法的 token
        return abort_err(401, login_target=request.path)

    # 如果都没问题，就返回 None
    return None


def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    return response


@cache.memoize(60)
def get_user(user_id) -> Users:
    return Users.query.filter(Users.id == user_id).first()
