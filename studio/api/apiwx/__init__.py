from flask import Blueprint, current_app, request
from flask_cors import CORS
from studio.models import db
from studio.utils import dfl, listf

from .jizhetuan import jizhetuan

apiwx = Blueprint("apiwx", __name__, url_prefix="/apiwx")
apiwx.register_blueprint(jizhetuan)

