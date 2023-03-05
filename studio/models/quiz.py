from .base import MixinBase, db


class QuizQuestions(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False, comment="问题内容")
