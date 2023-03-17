from flask import Blueprint, request, send_from_directory
from pandas import Series

from studio.models import db, EditorList, EditorWorks, EnrollDepts, EditorWorkFees
from studio.utils import dfln, dfl, ltd
from datetime import date
import pandas as pd
import numpy as np
import os

editorFee = Blueprint("editor", __name__, url_prefix="/editorFee")


@editorFee.route("/getEditors", methods=["GET"])
def r_get_editors():
    result = []
    for editor, deptName in db.session.query(EditorList, EnrollDepts.deptName). \
            outerjoin(EnrollDepts, EditorList.deptId == EnrollDepts.id).filter(EditorList.deleted == 0).all():
        # 对于每一个查询记录而言，__dict__方法可以将其转化为 Python 字典，但是会包括 _sa_instance_state 键，这个需要过滤掉
        # 这里是使用了连接查询, 使用 {**dict1, **dict2} 的方式来实现字典相加
        # 有一说一，不如直接写 SQL，详见 r_get_works 方法
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
    editor = EditorList(**dfl(dictReq, ["stuId", "editorName", "faculty", "tel", "cardId", "deptId"]))
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
    editor = EditorList.query.filter(EditorList.stuId == dictReq["stuId"], EditorList.deleted == 0).first()
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
    # 注意! 在 createWork 时还需要额外创建关系, 因此还需要额外操作 EditorWorkFees 表
    dictReq = request.get_json()["work"]
    work = EditorWorks(**dfl(dictReq, ["workName", "workFee", "note"]),
                       workDate=date.fromisoformat(dictReq["workDate"]))
    workAuthors = dictReq["authorList"]
    workEditors = dictReq["editorList"]
    # 计算稿酬
    authorPerFee = work.workFee * 0.8 / len(workAuthors)
    editorPerFee = work.workFee * 0.2 / len(workEditors)
    db.session.add(work)
    for workAuthor in workAuthors:
        author = EditorList.query.filter(EditorList.stuId == workAuthor["option"]["stuId"]).first()
        workFee = EditorWorkFees(editorType="作者", editorId=author.id, workId=work.id, workFee=authorPerFee)
        db.session.add(workFee)
    for workEditor in workEditors:
        editor = EditorList.query.filter(EditorList.stuId == workEditor["option"]["stuId"]).first()
        workFee = EditorWorkFees(editorType="编辑", editorId=editor.id, workId=work.id, workFee=editorPerFee)
        db.session.add(workFee)
    db.session.commit()
    return {"success": True}


@editorFee.route("/setWork", methods=["POST"])
def r_set_work():
    # 在修改稿件时，也需要修改稿件相关联的各类信息
    dictReq = request.get_json()["work"]
    work = EditorWorks.query.get(dictReq["id"])
    # 修改 EditorWorks 表
    for key, value in dfln(dictReq, ["id"]).items():
        if key == "workDate":
            setattr(work, key, date.fromisoformat(value))  # 对时间需要特殊处理
        else:
            setattr(work, key, value)
    # 修改 EditorWorkFees 表
    workFee = eval(dictReq["workFee"])
    workAuthors = dictReq["authorList"]
    workEditors = dictReq["editorList"]
    # 计算稿酬
    authorPerFee = workFee * 0.8 / len(workAuthors)
    editorPerFee = workFee * 0.2 / len(workEditors)
    # 先删除之前的关系
    workFees = EditorWorkFees.query.filter(EditorWorkFees.workId == work.__dict__["id"]).all()
    for workFee in workFees:
        db.session.delete(workFee)  # 对于关系而言，没有必要保留记录
    # 再创建新的关系
    for workAuthor in workAuthors:
        if "option" in workAuthor.keys():
            stuId = workAuthor["option"]["stuId"]
        else:
            stuId = workAuthor["stuId"]
        author = EditorList.query.filter(EditorList.stuId == stuId, EditorList.deleted == 0).first()
        workFee = EditorWorkFees(editorType="作者", editorId=author.id, workId=work.id, workFee=authorPerFee)
        db.session.add(workFee)
    for workEditor in workEditors:
        print(workEditor)
        if "option" in workEditor.keys():
            stuId = workEditor["option"]["stuId"]
        else:
            stuId = workEditor["stuId"]
        editor = EditorList.query.filter(EditorList.stuId == stuId, EditorList.deleted == 0).first()
        workFee = EditorWorkFees(editorType="编辑", editorId=editor.id, workId=work.id, workFee=editorPerFee)
        db.session.add(workFee)
    db.session.commit()
    return {"success": True}


@editorFee.route("/deleteWork", methods=["POST"])
def r_delete_work():
    dictReq = request.get_json()["work"]
    work = EditorWorks.query.get(dictReq["id"])
    # 注意，这里的处理是进行直接删除！为了确保数据库完整性，还需要将 WorkFees
    # 表的关联记录进行级联修改
    db.session.delete(work)
    fees = EditorWorkFees.query.filter(EditorWorkFees.workId == dictReq["id"]).all()
    for fee in fees:
        db.session.delete(fee)  # 对于关系而言, 没有必要保留历史记录
    db.session.commit()
    return {"success": True}


@editorFee.route("/getWorks", methods=["GET"])
def r_get_works():
    result = []
    # 该接口会查询 EditorWorkFees 表，查询与该 EditorWorks 相关的编者
    works = EditorWorks.query.filter(EditorWorks.deleted == 0).all()
    for work in works:
        # 这里不如写一个 SQL = =
        authorListSql = f"""SELECT editor_list.stuId, editor_list.editorName, editor_work_fees.workFee 
                        FROM editor_work_fees, editor_list 
                        WHERE editor_work_fees.editorId = editor_list.id 
                        AND editor_work_fees.workId = {work.id}
                        AND editor_work_fees.deleted = 0
                        AND editor_work_fees.editorType = '作者'"""
        authorList = db.session.execute(authorListSql).all()
        editorListSql = f"""SELECT editor_list.stuId, editor_list.editorName, editor_work_fees.workFee 
                        FROM editor_work_fees, editor_list 
                        WHERE editor_work_fees.editorId = editor_list.id 
                        AND editor_work_fees.workId = {work.id}
                        AND editor_work_fees.deleted = 0
                        AND editor_work_fees.editorType = '编辑'"""
        editorList = db.session.execute(editorListSql).all()
        result.append({
            **dfln(work.__dict__, ["_sa_instance_state", "workDate"]),
            "workDate": work.__dict__["workDate"].isoformat(),
            "authorList": [{**ltd(row, ["stuId", "editorName", "workFee"]),
                            "value": row[0], "label": f"{row[1]}({row[0]})"} for row in authorList],
            "editorList": [{**ltd(row, ["stuId", "editorName", "workFee"]),
                            "value": row[0], "label": f"{row[1]}({row[0]})"} for row in editorList],
        })
    result = sorted(result, key=lambda x: date.fromisoformat(x["workDate"]), reverse=True)
    return {"success": True, "works": result}


@editorFee.route("/getWorkFees", methods=["POST"])
def r_get_work_fees():
    # 该接口将按照起始时间和结束时间去查询所有的稿件，并计算稿费
    dictReq = request.get_json()["data"]
    startDate = date.fromisoformat(dictReq["startDate"])  # 查询起始时间
    endDate = date.fromisoformat(dictReq["endDate"])  # 查询结束时间
    # 注意，不同的数据库语言对时间的比较方法不同，这里写的是全表查询的SQL！存在优化的空间
    sql = """SELECT
                editor_works.workName,
                editor_works.workDate,
                editor_list.stuId,
                editor_list.cardId,
                editor_list.editorName,
                enroll_depts.deptName,
                editor_work_fees.workFee,
                editor_work_fees.editorType 
            FROM
                editor_work_fees
                LEFT JOIN editor_list ON editor_work_fees.editorId = editor_list.id
                LEFT JOIN editor_works ON editor_work_fees.workId = editor_works.id
                LEFT JOIN enroll_depts ON editor_list.deptId = enroll_depts.id 
            WHERE
                editor_work_fees.deleted = 0 
            ORDER BY
                editor_list.stuId DESC"""
    totalWorkFees = [
        ltd(row, ["workName", "workDate", "stuId", "cardId", "editorName", "deptName", "workFee", "editorType"])
        for row in db.session.execute(sql).all()]  # 执行全表查询
    queryWorkFees = pd.DataFrame(
        [row for row in totalWorkFees if startDate <= date.fromisoformat(str(row["workDate"])) <= endDate])
    # 注意，这里必须加上 str，以保证兼容性
    result = []
    if queryWorkFees.empty:  # 如果为空，返回空记录
        return {"success": True, "workFees": []}

    for name, group in queryWorkFees.groupby("editorName"):
        result.append({
            "editorName": name,
            "totalFees": sum(group["workFee"]),
            "stuId": group.iloc[0]["stuId"],
            "deptName": group.iloc[0]["deptName"],
            "cardId": group.iloc[0]["cardId"],
            "works": [{"workName": row["workName"], "editorType": row["editorType"], "fee": row["workFee"]}
                      for _, row in group.iterrows()]
        })
    return {"success": True, "workFees": result}


@editorFee.route("/uploadEditorWorks", methods=["POST"])
def r_upload_editor_works():
    file = request.files.getlist("file")[0]  # 仅接收一个文件
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    filename = file.filename
    file.save(f"tmp/{filename}")
    data = pd.read_excel(f"tmp/{filename}")
    data.fillna("", inplace=True)
    os.remove(f"tmp/{filename}")

    totalNotFoundLst = []
    totalWork = []
    try:
        # 先校验是否编辑/作者都在数据库
        for _, row in data.iterrows():
            workAuthors = [name.strip() for name in row["作者列表"].split(",") if name.strip() != '']
            workEditors = [name.strip() for name in row["编辑列表"].split(",") if name.strip() != '']
            if len(workAuthors) + len(workEditors) == 0:
                return {"success": False, "detail": f"{row['稿件名称']}: 作者和编辑数量为0！导入失败!"}
            if row["作者列表"].find("，") > -1 or row["编辑列表"].find("，") > -1:
                return {"success": False, "detail": f"{row['稿件名称']}: 在字段中发现中文逗号, 导入失败!"}

            notFoundEditors = []
            for name in list(set(workAuthors + workEditors)):
                if EditorList.query.filter(EditorList.editorName == name).first() is None:
                    notFoundEditors.append(name)
            totalNotFoundLst += notFoundEditors
        if len(totalNotFoundLst) > 0:
            return {"success": False,
                    "detail": f"下述编者尚未在数据库中，请先添加至数据库\n{', '.join(list(set(totalNotFoundLst)))}"}

        for _, row in data.iterrows():
            workFee = row["总稿酬"]
            work = EditorWorks(workName=row["稿件名称"], workDate=row["发布时间"], workFee=workFee,
                               note=str(row["备注"]))
            db.session.add(work)
            totalWork.append(work)

            workAuthors = [name.strip() for name in row["作者列表"].split(",") if name.strip() != '']
            workEditors = [name.strip() for name in row["编辑列表"].split(",") if name.strip() != '']

            authorPerFee = work.workFee * 0.8 / len(workAuthors)
            editorPerFee = work.workFee * 0.2 / len(workEditors)
            for workAuthor in workAuthors:
                author = EditorList.query.filter(EditorList.editorName == workAuthor, EditorList.deleted == 0).first()
                workFee = EditorWorkFees(editorType="作者", editorId=author.id, workId=work.id, workFee=authorPerFee)
                db.session.add(workFee)
            for workEditor in workEditors:
                editor = EditorList.query.filter(EditorList.editorName == workEditor, EditorList.deleted == 0).first()
                workFee = EditorWorkFees(editorType="编辑", editorId=editor.id, workId=work.id, workFee=editorPerFee)
                db.session.add(workFee)
        db.session.commit()
    except KeyError as ke:
        return {"success": False, "detail": f"缺少字段 [{ke.args[0]}]"}
    except Exception as e:
        print(e)
        return {"success": False, "detail": f"出现错误 [{e.args}]"}
    return {"success": True, "data": {"num": len(totalWork)}}


@editorFee.route("/getUploadEditorWorksFile", methods=["GET"])
def r_get_upload_editor_works_file():
    # 这里需要添加放行路由 /apivue/editorFees/getUpload
    return send_from_directory(os.getcwd() + "/examples", "example-editor-works.xlsx", as_attachment=True)


@editorFee.route("/uploadEditors", methods=["POST"])
def r_upload_editors():
    file = request.files.getlist("file")[0]  # 仅接收一个文件
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    filename = file.filename
    file.save(f"tmp/{filename}")
    data = pd.read_excel(f"tmp/{filename}", dtype=str)
    data.fillna("", inplace=True)
    os.remove(f"tmp/{filename}")

    totalEditor = []
    totalNotFoundLst = []
    totalDuplicateLst = []
    try:
        # 先校验一下是否有重复的学号，部门是否关联
        for _, row in data.iterrows():
            stuId = row["学号"]
            deptName = row["所属部门"]
            # 出现重复
            if EditorList.query.filter(EditorList.stuId == stuId, EditorList.deleted == 0).first() is not None:
                totalDuplicateLst.append(row["姓名"])
            # 部门不匹配
            if EnrollDepts.query.filter(EnrollDepts.deptName == deptName, EnrollDepts.deleted == 0) is None:
                totalNotFoundLst.append(row["所属部门"])

        print(totalDuplicateLst, totalNotFoundLst)
        detail = ""
        if len(totalDuplicateLst) > 0:
            detail += f"下述编者的学号出现重复, 请删除后再次上传!\n{', '.join(totalDuplicateLst)}\n"
        if len(totalNotFoundLst) > 0:
            detail += f"下述部门不存在，请在报名管理添加对应部门后再上传!\n{', '.join(totalNotFoundLst)}"
        if len(totalNotFoundLst) > 0 or len(totalDuplicateLst) > 0:
            return {"success": False, "detail": detail}

        # 数据校验无误，开始添加
        for _, row in data.iterrows():
            deptId = EnrollDepts.query.filter(EnrollDepts.deptName == row["所属部门"]).first().id
            editor = EditorList(stuId=row["学号"], editorName=row["姓名"], faculty=row["学院"], tel=row["电话"],
                                cardId=row["银行卡号"], deptId=deptId)
            totalEditor.append(editor)
            db.session.add(editor)
        db.session.commit()
    except KeyError as ke:
        return {"success": False, "detail": f"缺少字段 [{ke.args[0]}]"}
    except Exception as e:
        print(e)
        return {"success": False, "detail": f"出现错误 [{e.args}]"}
    return {"success": True, "data": {"num": len(totalEditor)}}


@editorFee.route("/getUploadEditorsFile", methods=["GET"])
def r_get_upload_editors_file():
    # 这里需要添加放行路由 /apivue/editorFees/getUpload
    return send_from_directory(os.getcwd() + "/examples", "example-editors.xlsx", as_attachment=True)
