from .base import MixinBase, db


class EditorList(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    # 由于数据库迁移发生部分错误，导致下述字段在云数据库中为手动创建，在本地的迁移记录中也不存在这些字段!
    stuId = db.Column(db.String(20), nullable=False, comment="学号")  # 该字段在云数据库中为手动创建!
    editorName = db.Column(db.String(20), nullable=False, comment="作者姓名")  # 该字段在云数据库中为手动创建!
    faculty = db.Column(db.String(20), nullable=True, comment="学部院")  # 该字段在云数据库中为手动创建!
    tel = db.Column(db.String(20), nullable=True, comment="联系电话")  # 该字段在云数据库中为手动创建!
    deptId = db.Column(db.Integer, db.ForeignKey("enroll_depts.id"), comment="所属部门ID")


class EditorWorkFees(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    editorType = db.Column(db.Enum("作者", "编辑"), nullable=False, default="作者")
    editorId = db.Column(db.Integer, nullable=False, comment="作者ID")
    workId = db.Column(db.Integer, nullable=False, comment="稿件ID")
    workFee = db.Column(db.DECIMAL(10, 5), nullable=True, comment="该作者/编辑在该作品中的应付稿酬")


class EditorWorks(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    workName = db.Column(db.Text, nullable=False, comment="作品名称")
    workDate = db.Column(db.Date, nullable=False, comment="发布时间")
    workFee = db.Column(db.DECIMAL(10, 5), nullable=False, comment="该作者/编辑在该作品中的应付稿酬")
    note = db.Column(db.Text, nullable=True, comment="其他信息")
