from flask import Blueprint,request
from sm4 import SM4Key
import requests
import base64
import json
from datetime import datetime

yuexun = Blueprint("yuexun",__name__)
SM_KEY = bytes.fromhex("918ba21cd1253de294b35394c58ad576")


@yuexun.route("/get_token",methods=["POST"])
def get_token():
    data = request.get_json()
    key = SM4Key(SM_KEY)
    sm4_pwd = base64.b64encode(key.encrypt(bytes(data["password"],encoding="utf-8"), padding=True)).decode("utf-8")
    print(sm4_pwd)
    login_req = requests.post("https://www.yuexunedu.com/store/api/v1.0/safetyLogin.json",data={
        "website":"https://www.yuexunedu.com/home/2.0/login/#/login",
        "username":data["username"],
        "password":sm4_pwd,
        "captchaUuid":"",
        "accountIdentityEnum":"2",
        "sessionUuid":""
    })
    return {"token":login_req.json()["datas"][0]["sessionUuid"]}
@yuexun.route("/get_classtable",methods=["POST"])
def get_classtable():
    data = request.get_json()
    class_id = requests.post("https://www.yuexunedu.com/store/api/v1.0/inquireFamilyStudentListAccount.json",data={"sessionUuid":data["token"]}).json()["datas"][0]["classId"]
    cur_week = requests.post("https://www.yuexunedu.com/store/api/v2.0/inquireSchoolWeekInfoTenant.json",data={"sessionUuid":data["token"]}).json()["datas"][0]["currWeek"]
    ct_req = requests.post("https://www.yuexunedu.com/store/api/v2.0/inquireGSStudentCourseListAccount.json",data={
        "sessionUuid":data["token"],
        "classId":class_id,
        "weekIndex":cur_week
    })
    ct_data = ct_req.json()["datas"][0]["courseList"]
    ct = {"Mon":[],"Tue":[],"Wed":[],"Thu":[],"Fri":[],"Sat":[],"Sun":[]}
    for i in ct_data: # 第i节课
        for j in i: #星期几
            courseTime = datetime.strptime(j["courseDay"],"%Y-%m-%d").strftime("%a") #星期几
            course = j["stuSectionCourseOutputList"][0]
            courseName = course["courseName"] #课程名
            startTime = course["startTime"] #开始时间
            endTime = course["endTime"] #结束时间
            ct[courseTime].append({
                "name":courseName,
                "start":startTime,
                "end":endTime
            })
    return ct            