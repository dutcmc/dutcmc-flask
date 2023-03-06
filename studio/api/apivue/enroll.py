import json

import datetime
from sqlalchemy import or_, and_
from flask import Blueprint, request, send_file
from studio.models import EnrollCandidates, EnrollDepts, EnrollTurns, db
from studio.utils import dfl, dfln, listf

enroll = Blueprint("enroll", __name__, url_prefix="/enroll")


@enroll.route("/getDepts", methods=["GET"])
def r_get_depts():
    depts = EnrollDepts.query.filter(EnrollDepts.deleted == 0).all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in depts]
    return {"depts": result}


@enroll.route("/getDeletedDepts", methods=["GET"])
def r_get_deleted_depts():
    depts = EnrollDepts.query.filter(EnrollDepts.deleted == 1).all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in depts]
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
    turns = EnrollTurns.query.filter(EnrollTurns.deleted == 0).all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in turns]
    return {"turns": result}


@enroll.route("/getDeletedTurns", methods=["GET"])
def r_get_deleted_turns():
    turns = EnrollTurns.query.filter(EnrollTurns.deleted == 1).all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in turns]
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
        # 存在当前批次的重复记录
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
        # 在当前报名批次中有相同的报名表
        t = queryCandidate.update_time + datetime.timedelta(hours=8)
        return {"unique": False, "time": t.strftime("%Y-%m-%d %H:%M:%S")}


@enroll.route("/getEnrollList", methods=["POST"])
def r_get_enroll_list():
    # 先确认批次没有被删除
    turnId = request.get_json()["turnId"]
    # turnData = db.session.query(EnrollTurns.id).filter(turnId == EnrollTurns.id)
    # if turnData.deleted:
    #     return {"enrollCandidates": []}
    # 开始查询
    queryData = EnrollCandidates.query
    if turnId > 0:
        candidates = queryData.filter(EnrollCandidates.turnId == turnId, EnrollCandidates.deleted == 0).all()
    else:
        candidates = queryData.all()
    result = [dfln(row.__dict__, ["_sa_instance_state"]) for row in candidates]
    return {"enrollCandidates": result}


