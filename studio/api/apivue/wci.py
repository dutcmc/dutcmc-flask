from flask import Blueprint, request
import pandas as pd
import os

wci = Blueprint("wci", __name__, url_prefix="/wci")


@wci.route("/parseData", methods=["POST"])
def r_parse_data():
    file = request.files.getlist("file")[0]  # 仅接收一个文件
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    filename = file.filename
    file.save(f"tmp/{filename}")
    data = pd.read_excel(f"tmp/{filename}", skipfooter=1)
    result = []
    accounts = []
    for name, group in data.groupby("公众号"):
        accounts.append({
            "value": name,
            "label": name
        })
        for _, row in group.iterrows():
            result.append({
                "account": row["公众号"],
                "title": row["标题"],
                "datetime": row["发布时间"],
                "R": row["阅读数"],
                "Z": row["在看数"],
                "L": row["点赞数"]
            })
    os.remove(f"tmp/{filename}")
    return {"success": True, "data": result, "accounts": accounts}
