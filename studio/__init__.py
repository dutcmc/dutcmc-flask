import os
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from studio.models import db
from .api.apivue import apivue
from .api.apiwx import apiwx
from .utils import cache
from .utils.interceptor import global_interceptor, after_request


def create_app():
    app = Flask(__name__)

    load_dotenv(override=True)

    # 数据库配置
    windows_os = sys.platform.startswith("win")
    db_user = os.getenv("MYSQL_USER")
    db_pwd = os.getenv("MYSQL_PASSWORD")
    db_host = os.getenv("MYSQL_HOST")
    db_name = os.getenv("MYSQL_DATABASE")

    if windows_os:
        prefix = "sqlite:///"
    else:
        prefix = "sqlite:////"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if app.debug:
        app.config["SQLALCHEMY_DATABASE_URI"] = prefix + "../data/data.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = \
            f"mysql+pymysql://{db_user}:{db_pwd}@{db_host}/{db_name}"

    # 导入 JWT_KEY
    app.config["JWT_KEY"] = os.getenv("JWT_KEY")
    # 初始化插件
    db.init_app(app)
    cache.init_app(app)
    # 添加数据库迁移
    migrate = Migrate()
    migrate.init_app(app, db)
    # 添加拦截器, 进行用户鉴权
    app.before_request(global_interceptor)
    # app.after_request(after_request)
    # 注册一级蓝图
    app.register_blueprint(apivue)
    app.register_blueprint(apiwx)
    # 注册根路由
    app.add_url_rule("/", view_func=lambda: "This is DUTCMC backstage server.")
    return app
