from flask import Blueprint, request
from studio.models import db, EditorList, EditorWorks, EnrollDepts
from studio.utils import dfln

editorFee = Blueprint("editor", __name__, url_prefix="/editorFee")


@editorFee.route("/getEditors", methods=["GET"])
def r_get_editors():
    result = []
    for editor, deptName in db.session.query(EditorList, EnrollDepts.deptName).\
            outerjoin(EnrollDepts, EditorList.deptId == EnrollDepts.id).all():
        # 对于每一个查询记录而言，__dict__方法可以将其转化为 Python 字典，但是会包括 _sa_instance_state 键，这个需要过滤掉
        # 这里是使用了连接查询, 使用 {**dict1, **dict2} 的方式来实现字典相加
        result.append({**dfln(editor.__dict__, ["_sa_instance_state"]), "deptName": deptName})
    result = sorted(result, key=lambda x: x["id"], reverse=True)
    return {"success": True, "editors": result}


@editorFee.route("/getDeletedEditors", methods=["GET"])
def r_get_deleted_editors():
    editors = EditorList.query.filter(EditorList.deleted == 1).all()
    result = [dlfn(row.__dict__, ["_sa_instance_state"]) for row in editors]
    return {"success": True, "editors": result}


@editorFee.route("/recoverEditor", methods=["POST"])
def r_recover_editor():
    dictReq = request.get_json()["editor"]
    editor = EditorList.query.get(dictReq["id"])
    editor.deleted = 0
    db.session.commit()


@editorFee.route("/createEditor", methods=["POST"])
def r_create_editor():
    dictReq = request.get_json()["editor"]
    editor = EditorList(**dfl(dictReq, ["stuId", "editorName", "faculty", "tel", "deptId"]))
    sameEditor = EditorList.query.get(dictReq["stuId"])
    if sameEditor is not None:
        return {"success": False, "detail": "存在学号相同的作者/编辑"}
    db.session.add(editor)
    db.session.commit()
    return {"success": True}


@editorFee.route("/setEditor", methods=["POST"])
def r_set_editor():
    dictReq = request.get_json()["editor"]
    editor = EditorList.query.get(dictReq["id"])
    if editor is None:
        return {"success": False, "detail": "找不到指定id的作者/编辑"}
    # 设置除了 id 以外的属性
    for key, value in dfln(dictReq, ["id"]).items():
        setattr(editor, key, value)
    db.session.commit()
    return {"success": True}
