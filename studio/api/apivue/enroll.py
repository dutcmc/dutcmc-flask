import json

import datetime
from sqlalchemy import or_, and_
from flask import Blueprint, request, send_file
from studio.models import EnrollCandidates, EnrollDepts, EnrollTurns, db
from studio.utils import dfl, listf

enroll = Blueprint("enroll", __name__, url_prefix="/enroll")


@enroll.route("/getDepts", methods=["GET"])
def r_get_depts():
    depts = db.session.query(EnrollDepts.id, EnrollDepts.deptName).filter(EnrollDepts.deleted == 0).all()
    result = []
    for dept in depts:
        result.append({
            "id": dept.id,
            "deptName": dept.deptName
        })
    return {"depts": result}


@enroll.route("/getDeletedDepts", methods=["GET"])
def r_get_deleted_depts():
    depts = db.session.query(EnrollDepts.id, EnrollDepts.deptName).filter(EnrollDepts.deleted == 1).all()
    result = []
    for dept in depts:
        result.append({
            "id": dept.id,
            "deptName": dept.deptName
        })
    return {"depts": result}


@enroll.route("/recoverDept", methods=["POST"])
def r_recover_dept():
    dept = request.get_json()["dept"]
    enrollDept = EnrollDepts.query.get(dept["id"])
    enrollDept.deleted = 0
    db.session.commit()
    return {"success": True}


@enroll.route("/setDept", methods=["POST"])
def r_set_dept():
    dept = request.get_json()["dept"]
    enrollDept = EnrollDepts.query.get(dept["id"])
    enrollDept.deptName = dept["deptName"]
    db.session.commit()
    return {"success": True}


@enroll.route("/deleteDept", methods=["POST"])
def r_delete_dept():
    dept = request.get_json()["dept"]
    enrollDept = EnrollDepts.query.get(dept["id"])
    enrollDept.deleted = 1
    db.session.commit()
    return {"success": True}


@enroll.route("/createDept", methods=["POST"])
def r_create_dept():
    dictReq = request.get_json()["dept"]
    dept = EnrollDepts(deptName=dictReq["deptName"])
    db.session.add(dept)
    db.session.commit()
    return {"success": True}


@enroll.route("/getTurns", methods=["GET"])
def r_get_turns():
    turns = db.session.query(EnrollTurns.id, EnrollTurns.turnName, EnrollTurns.activated).filter(
        EnrollTurns.deleted == 0).all()
    result = []
    for turn in turns:
        result.append({
            "id": turn.id,
            "turnName": turn.turnName,
            "activated": turn.activated
        })
    return {"turns": result}


@enroll.route("/getDeletedTurns", methods=["GET"])
def r_get_deleted_turns():
    turns = db.session.query(EnrollTurns.id, EnrollTurns.turnName, EnrollTurns.activated).filter(
        EnrollTurns.deleted == 1).all()
    result = []
    for turn in turns:
        result.append({
            "id": turn.id,
            "turnName": turn.turnName,
            "activated": turn.activated
        })
    return {"turns": result}


@enroll.route("/recoverTurn", methods=["POST"])
def r_recover_turn():
    turn = request.get_json()["turn"]
    enrollTurn = EnrollTurns.query.get(turn["id"])
    enrollTurn.deleted = 0
    db.session.commit()
    return {"success": True}


@enroll.route("/setTurn", methods=["POST"])
def r_set_turn():
    turn = request.get_json()["turn"]
    enrollTurn = EnrollTurns.query.get(turn["id"])
    enrollTurn.turnName = turn["turnName"]
    enrollTurn.activated = turn["activated"]
    db.session.commit()
    return {"success": True}


@enroll.route("/deleteTurn", methods=["POST"])
def r_delete_turn():
    turn = request.get_json()["turn"]
    enrollTurn = EnrollTurns.query.get(turn["id"])
    enrollTurn.deleted = 1
    enrollTurn.activated = 0
    db.session.commit()
    return {"success": True}


@enroll.route("/createTurn", methods=["POST"])
def r_create_turn():
    dictReq = request.get_json()["turn"]
    turn = EnrollTurns(turnName=dictReq["turnName"])
    turn.activated = 0
    db.session.add(turn)
    db.session.commit()
    return {"success": True}


@enroll.route("/submit", methods=["POST"])
def r_submit():
    dictReq = request.get_json()
    enrollCandidate = EnrollCandidates(
        **dfl(dictReq, ["stuId", "name", "sex", "faculty", "tel",
                        "firstChoice", "secondChoice", "thirdChoice", "allowAdjust", "info", "turnId"])
    )
    queryCandidate = db.session.query(EnrollCandidates) \
        .filter(and_(EnrollCandidates.stuId == enrollCandidate.stuId, EnrollCandidates.deleted == 0,
                     EnrollCandidates.turnId == enrollCandidate.turnId)).first()
    if queryCandidate is None:
        db.session.add(enrollCandidate)
        db.session.commit()
    else:
        # ?????????????????????????????????
        queryCandidate.deleted = 1
        db.session.add(enrollCandidate)
        db.session.commit()
    return {"success": True}


@enroll.route("/verifyUnique", methods=["POST"])
def r_verify_unique():
    dictReq = request.get_json()["info"]
    stuId = dictReq["stuId"]
    name = dictReq["name"]
    turnId = dictReq["turnId"]
    queryCandidate = db.session.query(EnrollCandidates) \
        .filter(and_(EnrollCandidates.stuId == stuId,
                     EnrollCandidates.turnId == turnId)).first()
    if queryCandidate is None:
        return {"unique": True}
    else:
        # ?????????????????????????????????????????????
        t = queryCandidate.update_time + datetime.timedelta(hours=8)
        return {"unique": False, "time": t.strftime("%Y-%m-%d %H:%M:%S")}


@enroll.route("/getEnrollList", methods=["POST"])
def r_get_enroll_list():
    # ??????????????????????????????
    turnId = request.get_json()["turnId"]
    # turnData = db.session.query(EnrollTurns.id).filter(turnId == EnrollTurns.id)
    # if turnData.deleted:
    #     return {"enrollCandidates": []}
    # ????????????
    queryData = db.session.query(EnrollCandidates)
    if turnId > 0:
        candidates = queryData.filter(EnrollCandidates.turnId == turnId, EnrollCandidates.deleted == 0).all()
    else:
        candidates = queryData.all()
    result = []
    for candidate in candidates:
        result.append({
            "id": candidate.id,
            "stuId": candidate.stuId,
            "name": candidate.name,
            "sex": candidate.sex,
            "faculty": candidate.faculty,
            "tel": candidate.tel,
            "allowAdjust": candidate.allowAdjust,
            "firstChoice": candidate.firstChoice,
            "secondChoice": candidate.secondChoice,
            "thirdChoice": candidate.thirdChoice,
            "info": candidate.info,
            "turnId": candidate.turnId
        })
    return {"enrollCandidates": result}


