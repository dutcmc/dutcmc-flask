from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})


def dfc(dictA: dict, classK: object):
    """Utils: dict filter by class."""
    return {k: v for k, v in dictA.items() if hasattr(classK, k)}


def dfd(dictA: dict, dictK: dict):
    """Utils: dict filter by dict with default value."""
    return {k: dictA.get(k) or v for k, v in dictK.items()}


def dfl(dictA: dict, lstK: list):
    """Utils: dict filter by list."""
    return {k: v for k, v in dictA.items() if k in lstK}


def dfln(dictA: dict, lstK: list = []):
    """Utils: dict filter by not list."""
    lstK += ["create_time", "update_time", "update_cnt", "deleted"]
    return {k: v for k, v in dictA.items() if k not in lstK}


def listf(lstA: list):
    """Utils: flat the list, 将列表每一项展开"""
    return [x[0] for x in lstA]


def ltd(lstA: list, lstB: list):
    """Utils: list to dict, 按照 listB 的键名将 listA 的各个值封装为字典"""
    result = dict()
    [result.__setitem__(key, value) for key, value in zip(lstB, lstA)]
    return result


def abort_err(code: int, details: str = None, **kwargs):
    dictDesc = {
        401: "需要登录",
        403: "权限不足",
        461: "账号需要验证",
        462: "登录失败",
        463: "登录过期",
        471: "参数错误",
        472: "参数未知",
        532: "数据库数据错误",
        533: "数据库完整性错误",
        541: "数据库查询应有但没有结果",
    }
    return {"success": False, "details": details or dictDesc[code], **kwargs}, code


