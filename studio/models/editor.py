from .base import MixinBase, db


class EditorList(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    stuId = db.Column(db.String(20), nullable=False, comment="学号")
    editorName = db.Column(db.String(20), nullable=False, comment="作者姓名")
    faculty = db.Column(db.String(20), nullable=True, comment="学部院")
    tel = db.Column(db.String(20), nullable=True, comment="联系电话")
    deptId = db.Column(db.Integer, db.ForeignKey("enroll_depts.id"), comment="所属部门ID")


class EditorWorks(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    workName = db.Column(db.Text, nullable=False, comment="作品名称")
    editorType = db.Column(db.Enum("作者", "编辑"), nullable=False, default="作者")
    editorId = db.Column(db.Integer, nullable=False, comment="作者ID")
    workDate = db.Column(db.Date, nullable=False, comment="发布时间")
    workFee = db.Column(db.DECIMAL(10, 5), nullable=False, comment="该作者/编辑在该作品中的应付稿酬")
