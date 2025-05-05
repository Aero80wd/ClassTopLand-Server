from .yuexun import yuexun
from flask import Blueprint
export_api = Blueprint("export_api",__name__)
@export_api.route("/list")
def list():
    return {"code":200,"msg":"success","data":[
        {"name":"悦讯（一起成长）","id":"yuexun"}
    ]}