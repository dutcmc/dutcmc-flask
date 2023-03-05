from flask import Blueprint, request
import pandas as pd
import numpy as np
import os

wci = Blueprint("wci", __name__, url_prefix="/wci")


def calcWCI(R: [], Z: [], L: [], Rt: int, Zt: int, Lt: int, d: int):
    n = len(R)
    mR = np.max(R)
    mZ = np.max(Z)
    mL = np.max(L)
    tR = np.sum(R)
    tZ = np.sum(Z)
    tL = np.sum(L)

    O = 0.85 * np.log(tR / d + 1) + 0.09 * np.log(tZ / d * 10 + 1) + 0.06 * np.log(tL / d * 10 + 1)
    A = 0.85 * np.log(tR / n + 1) + 0.09 * np.log(tZ / n * 10 + 1) + 0.06 * np.log(tL / n * 10 + 1)
    H = 0.85 * np.log(Rt / d + 1) + 0.09 * np.log(Zt / d * 10 + 1) + 0.06 * np.log(Lt / d * 10 + 1)
    P = 0.85 * np.log(mR + 1) + 0.09 * np.log(mZ * 10 + 1) + 0.06 * np.log(mL * 10 + 1)
    return np.power(0.6 * O + 0.2 * A + 0.1 * H + 0.1 * P, 2) * 12


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
                "L": row["点赞数"],
                "seq": row["文章序号"]
            })
    os.remove(f"tmp/{filename}")
    return {"success": True, "data": result, "accounts": accounts}


@wci.route("/calcWCI", methods=["POST"])
def r_calc_wci():
    result = []
    dictReq = request.get_json()["data"]
    d = request.get_json()["d"]
    df = pd.DataFrame(dictReq).drop(["id"], axis=1)
    for name, group in df.groupby("account"):
        relatePassages = df.loc[df["relateAccount"] == name]
        firstPassages = group.loc[df["seq"] == 1]  # 获取原有头条数
        # 更新各个权重
        relatePassages["R"] = relatePassages["R"] * relatePassages["weight"] / 100
        relatePassages["L"] = relatePassages["L"] * relatePassages["weight"] / 100
        relatePassages["Z"] = relatePassages["Z"] * relatePassages["weight"] / 100

        totalPassages = pd.concat([group, relatePassages])
        Rt = np.sum(firstPassages["R"])  # 头条总阅读量
        Lt = np.sum(firstPassages["L"])  # 头条总点赞量
        Zt = np.sum(firstPassages["Z"])  # 头条总在看量
        R = totalPassages["R"].to_numpy()
        Z = totalPassages["Z"].to_numpy()
        L = totalPassages["L"].to_numpy()
        result.append({"account": name, "wci": calcWCI(R, Z, L, Rt, Zt, Lt, d)})
    result = sorted(result, key=lambda x: x["wci"], reverse=True)
    return {"success": True, "data": result}
