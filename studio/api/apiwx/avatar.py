from flask import Blueprint, request

from studio.models import WxAvatarsImage

avatar = Blueprint("avatar", __name__, url_prefix="/avatar")


@avatar.route("/getAvatarImages", methods=["GET"])
def r_get_avatar_images():
    avatarImages = WxAvatarsImage.query.all()
    result = []
    for avatarImage in avatarImages:
        result.append({"id": avatarImage.id, "src": avatarImage.src, "selected": avatarImage.selected, "iswide": avatarImage.isWide})
    return {"imgList": result, "imgCount": len(avatarImages)}

@avatar.route("/getAvatarImages_415", methods=["GET"])
def r_get_avatar_images_415():
    avatarImages = WxAvatarsImage_415.query.all()
    result = []
    for avatarImage in avatarImages:
        result.append({"id": avatarImage.id, "src": avatarImage.src, "selected": avatarImage.selected, "iswide": avatarImage.isWide})
    return {"imgList": result, "imgCount": len(avatarImages)}
