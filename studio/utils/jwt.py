import jwt
from flask import current_app
from datetime import datetime, timedelta, timezone


def create_token(payload):
    # token 有效时长为 1 个小时
    payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=3600)
    token = jwt.encode(payload, key=current_app.config["JWT_KEY"], algorithm="HS512")
    # 记录 token 至日志
    current_app.logger.info(f"user: {token}")
    return token


def load_token(token):
    try:
        print(token)
        payload = jwt.decode(token, key=current_app.config["JWT_KEY"], algorithms=["HS512"])
        current_app.logger.info(f"payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        # token 过期
        return "ExpiredSignature"
    except jwt.DecodeError:
        # token 认证失败
        return None
    except jwt.InvalidTokenError:
        # token 非法
        return None
