from flask import Blueprint, request

from studio.models import WxAvatarsImage

avatar = Blueprint("avatar", __name__, url_prefix="/avatar")


@avatar.route("/getAvatarImages", methods=["GET"])
def r_get_avatar_images():
    avatarImages = WxAvatarsImage.query.all()
    result = []
    for avatarImage in avatarImages:
        result.append({"src": avatarImage.src, "selected": avatarImage.selected})
    return {"imgList": result, "imgCount": len(avatarImages)}
