from studio import create_app
from studio.models import db, EnrollDepts, EnrollTurns, Users
from flask_cors import CORS

app = create_app()
CORS(app, supports_credentials=True, resources=r"/*")


def db_create_all():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(EnrollDepts(deptName="技术部"))
        db.session.add(EnrollTurns(turnName="测试招新", activated=1))
        db.session.add(Users(username="dutcmc", password="dllgdx84708170"))
        db.session.commit()


if __name__ == '__main__':
    # db_create_all()
    app.run(debug=True, port=3000)

