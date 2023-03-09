from flask import Blueprint, request
from studio.models import db, EditorList, EditorWorks, EnrollDepts, EditorWorkFees
from studio.utils import dfln, dfl

editorFee = Blueprint("editor", __name__, url_prefix="/editorFee")


@editorFee.route("/getEditors", methods=["GET"])
def r_get_editors():
    result = []
    for editor, deptName in db.session.query(EditorList, EnrollDepts.deptName). \
            outerjoin(EnrollDepts, EditorList.deptId == EnrollDepts.id).filter(EditorList.deleted == 0).all():
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
    return {"success": True}


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
    # if editor is None:
    #     return {"success": False, "detail": "找不到指定id的作者/编辑"}
    # 设置除了 id 以外的属性
    for key, value in dfln(dictReq, ["id"]).items():
        setattr(editor, key, value)
    db.session.commit()
    return {"success": True}


@editorFee.route("/verifyUniqueEditor", methods=["POST"])
def r_verify_unique_editor():
    dictReq = request.get_json()["editor"]
    id = dictReq.get("id")
    editor = EditorList.query.filter(EditorList.stuId == dictReq["stuId"]).first()
    if editor is None:  # 如果找不到匹配的，显然是唯一的，这包括两种情况: 1. 新建的作者 2. 将原有的作者学号修改了
        return {"success": True, "unique": True}
    elif editor.id == id:  # 是同一条编辑记录，这意味着是同一个作者，但是学号变更了
        return {"success": True, "unique": True}
    else:  # 出现重复
        return {"success": True, "unique": False, "detail": editor.editorName}


@editorFee.route("/deleteEditor", methods=["POST"])
def r_delete_editor():
    dictReq = request.get_json()["editor"]
    editor = EditorList.query.get(dictReq["id"])
    # if editor is None:
    #     return {"success": False, "detail": "未找到指定作者"}
    # else:
    editor.deleted = 1
    db.session.commit()
    return {"success": True}


@editorFee.route("/createWork", methods=["POST"])
def r_create_work():
    dictReq = request.get_json()["work"]
    work = EditorWorks(**dfl(dictReq, ["workName", "workDate", "workFee", "note"]))
    db.session.add(work)
    db.session.commit()
    return {"success": True}


@editorFee.route("/setWork", methods=["POST"])
def r_set_work():
    dictReq = request.get_json()["work"]
    work = EditorWorks.query.get(dictReq["id"])
    for key, value in dfln(dictReq, ["id"]).items():
        setattr(work, key, value)
    db.session.commit()
    return {"success": True}


@editorFee.route("/deleteWork", methods=["POST"])
def r_delete_work():
    dictReq = request.get_json()["work"]
    work = EditorWorks.query.get(dictReq["id"])
    # 注意，在删除时，仅仅是将 deleted 改为 1，为了确保数据库完整性，还需要将 WorkFees
    # 表的关联记录进行级联修改
    work.deleted = 1
    fees = EditorWorkFees.query.filter(EditorWorkFees.workId == dictReq["id"]).all()
    for fee in fees:
        fee.deleted = 1
    db.session.commit()
    return {"success": True}


@editorFee.route("/recoverWork", methods=["POST"])
def r_recover_work():
    dictReq = request.get_json()["work"]
    work = EditorWorks.query.get(dictReq["id"])
    work.deleted = 0
    fees = EditorWorkFees.query.filter(EditorWorkFees.workId == dictReq["id"]).all()
    for fee in fees:
        fee.deleted = 0
    db.session.commit()
    return {"success": True}


@editorFee.route("/getWorks", methods=["GET"])
def r_get_works():
    result = []
    # 该接口会查询 EditorWorkFees 表，查询与该 EditorWorks 相关的编者
    works = EditorWorks.query.filter(EditorWorks.deleted == 0).all()
    for work in works:
        fees = EditorWorkFees.query.filter(EditorWorkFees.workId == work.id).all()
        result.append({
            **dfln(work.__dict__, ["_sa_instance_state"]),
            "fees": [dlfn(row.__dict__, ["_sa_instance_state"]) for row in fees]
        })
    return {"success": True}


@editorFee.route("/getDeletedWorks", methods=["GET"])
def r_get_deleted_works():
    # 该接口不返回关联的详细信息
    works = EditorWorks.query.filter(EditorWorks.deleted == 1).all()
    result = [dlfn(row.__dict__, ["_sa_instance_state"]) for row in works]
    return {"success": True, "works": result}


@editorFee.route("/createWorkFee", methods=["POST"])
def r_create_work_fee():
    dictReq = request.get_json()["workFee"]
    workFee = EditorWorkFees(**dfl(dictReq, ["editorType", "editorId", "workId", "workFee"]))
    db.session.add(workFee)
    db.session.commit()
    return {"success": True}


@editorFee.route("/setWorkFee", methods=["POST"])
def r_set_work_fee():
    dictReq = request.get_json()["workFee"]
    workFee = EditorWorkFees.query.get(dictReq["id"])
    for key, value in dfln(dictReq, ["id"]).items():
        setattr(workFee, key, value)
    db.session.commit()
    return {"success": True}


@editorFee.route("/deleteWorkFee", methods=["POST"])
def r_delete_work_fee():
    dictReq = request.get_json()["workFee"]
    workFee = EditorWorkFees.query.get(dictReq["id"])
    workFee.deleted = 1
    db.session.commit()
    return {"success": True}


@editorFee.route("/recoverWorkFee", methods=["POST"])
def r_recover_work_fee():
    dictReq = request.get_json()["workFee"]
    workFee = EditorWorkFees.query.get(dictReq["id"])
    workFee.deleted = 0
    db.session.commit()
    return {"success": True}


@editorFee.route("/getWorkFees", methods=["GET"])
def r_get_work_fees():
    # 该接口会进行一次关联查询，仅与 EditorList 表作关联查询
    result = []
    workFees = EditorWorkFees.query.filter(EditorWorkFees.deleted == 0).all()
    for workFee in workFees:
        editor = EditorList.query.filter(EditorList.id == workFee.editorId).first()
        result.append({
            **dfl(workFee.__dict__, ["_sa_instance_state"]),
            **dfl(editor.__dict__, ["_sa_instance_state", "id"])
        })
    return {"success": True}


@editorFee.route("/getDeletedWorkFees", methods=["GET"])
def r_get_deleted_work_fees():
    # 该接口不返回关联的详细信息
    workFees = EditorWorkFees.query.filter(EditorWorkFees.deleted == 1).all()
    result = [dlfn(row.__dict__, ["_sa_instance_state"]) for row in workFees]
    return {"success": True, "workFees": result}
