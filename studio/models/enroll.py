from .base import MixinBase, db


class EnrollTurns(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    turnName = db.Column(db.String(40), nullable=False, comment="招新批次名称")
    activated = db.Column(db.Integer, nullable=False, comment="是否为当前批次", server_default=db.text("0"))


class EnrollCandidates(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    stuId = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    faculty = db.Column(db.String(20), nullable=False)
    firstChoice = db.Column(db.String(20), nullable=False, comment="第一志愿")
    secondChoice = db.Column(db.String(20), nullable=True, comment="第二志愿")
    thirdChoice = db.Column(db.String(20), nullable=True, comment="第三志愿")
    tel = db.Column(db.String(20), nullable=False, comment="联系电话")
    allowAdjust = db.Column(db.Boolean, nullable=False, comment="是否服从调剂")
    info = db.Column(db.Text, nullable=True, comment="特长等详细信息")
    turnId = db.Column(db.Integer, db.ForeignKey("enroll_turns.id"))


class EnrollDepts(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    deptName = db.Column(db.String(20), nullable=False, comment="部门名称")
    deptInfo = db.Column(db.Text, nullable=True, comment="部门简介")
