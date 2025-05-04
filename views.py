from flask import Blueprint,request,jsonify,url_for
from models import db,User,Class,Role,Student
import hashlib
from functools import wraps
from flask_mail import Mail,Message
from flask import current_app
from threading import Thread
from flask import render_template
mail = Mail()
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message("[ClassTopLand]" + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
def token_required(f):
    """
    装饰器函数，用于验证用户的token是否正确。

    该装饰器会从请求头中获取token，然后通过token查询对应的用户。
    如果用户存在且token正确，则允许执行被装饰的函数；否则，返回错误信息。

    参数:
        f (function): 被装饰的函数。

    返回值:
        function: 装饰后的函数。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头中获取token
        token = request.headers.get('token')
        if not token:
            return jsonify({'code':403,'message': '缺少Token！'}), 401

        # 通过token查询对应的用户
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({'code':403,'message': 'Token无效！'}), 401

        # 将用户对象作为参数传递给被装饰的函数
        return f(user, *args, **kwargs)
    return decorated

bp = Blueprint('views',__name__)
@bp.route("/register",methods=['POST'])
def register():
    if len(User.query.all()) == 0:
        user_role = Role.query.filter_by(name="Admin").first()
    else:
        if request.headers.get("token"):
            user = User.query.filter_by(token=request.headers.get("token")).first()
            if user.role == Role.query.filter_by(name="Admin").first().id:
                if request.json.get("role"):
                    user_role = Role.query.filter_by(name=request.json.get("role")).first()
                    if not user_role:
                        return {"code":400,"msg":"角色未找到"}
            else:
                user_role = Role.query.filter_by(name="User").first()
        else:
            user_role = Role.query.filter_by(name="User").first()
    new_user = User(request.json.get("name"),request.json.get("password"),user_role.id,request.json.get("qq"))
    db.session.add(new_user)
    db.session.commit()
    confirm_url = url_for("userviews.confirm_redirect",token=new_user.generate_confirm_token(),_external=True)
    send_email(request.json.get("qq") + "@qq.com","验证你的账户","email/confirm",user=new_user,confirm_url=confirm_url)
    return {"code":200,"msg":"ok"}
@bp.route("/get_token",methods=['POST'])
def get_token():
    name = request.json.get("name")
    password = request.json.get("password")
    user = User.query.filter_by(name=name).first()
    if user:
        h = hashlib.sha256()
        h.update(password.encode('utf-8'))
        if user.password == h.hexdigest():
            if (not user.iscomfirm):
                return {"code":400,"msg":"用户未验证"}
            return {"code":200,"msg":"ok","token":user.token}
        else:
            return {"code":400,"msg":"密码错误"}
    else:
        return {"code":400,"msg":"用户未找到"}

@bp.route("/get_userinfo",methods=['GET'])
@token_required
def get_userinfo(user : User):
    return {"code":200,"msg":"ok","id":user.id,"name":user.name,"role":user.role,"qq":user.qq,"role_name":Role.query.filter_by(id=user.role).first().name}
@bp.route("/is_true_token",methods=['POST'])
def is_true_token():
    token = request.json.get("token")
    user = User.query.filter_by(token=token).first()
    if user and user.iscomfirm == True:
        return {"code":200,"msg":"ok"}
    else:
        return {"code":400,"msg":"Token无效"}
# Class Mange
@bp.route("/add_class",methods=['POST'])
@token_required
def add_class(user):
    try:
        new_class = Class(request.json.get("name"),user.id)
        db.session.add(new_class)
        db.session.commit()
    except:
        print("error")
        db.session.rollback()
        return {"code":400,"msg":"班级名称已存在"}
    
    return {"code":200,"msg":"ok"}

@bp.route("/get_class",methods=['POST'])
@token_required
def get_class(user):
    if user.role == Role.query.filter_by(name="Admin").first().id:
        print("it's admin")
        classes = Class.query.all()
    else:
        classes = Class.query.filter_by(byuser=user.id)
    # type(User.query.filter_by(id=Class.query.first().byuser).first())
    return {"code":200,"msg":"ok","data":[{"id":c.id,"name":c.name,"byuser":c.byuser,"byusername":(User.query.filter_by(id=c.byuser).first().name)} for c in classes]}
@bp.route("/get_class_info",methods=['POST'])
@token_required
def get_class_info(user):
    if user.role == Role.query.filter_by(name="Admin").first().id:
        classes = Class.query.filter_by(id=request.json.get("class")).first()
    else:
        if Class.query.filter_by(id=request.json.get("class")).first().byuser == user.id:
            classes = Class.query.filter_by(id=request.json.get("class")).first()
        else:
            return {"code":400,"msg":"你不是该班级的教师"}
    return {"code":200,"msg":"ok","data":{"id":classes.id,"name":classes.name,"byuser":classes.byuser}}
@bp.route("/delete_class",methods=['POST'])
@token_required
def delete_class(user):
    if user.role == Role.query.filter_by(name="Admin").first().id:
        classes = Class.query.filter_by(id=request.json.get("class")).first()
    else:
        if Class.query.filter_by(id=request.json.get("class")).first().byuser == user.id:
            classes = Class.query.filter_by(id=request.json.get("class")).first()
        else:
            return {"code":400,"msg":"你不是该班级的教师"}
    if not classes:
        return {"code":400,"msg":"班级不存在"}
    db.session.delete(classes)
    db.session.commit()
    return {"code":200,"msg":"ok"}
@bp.route("/get_class_student",methods=['POST'])
@token_required
def get_class_student(user):
    if user.role == Role.query.filter_by(name="Admin").first().id:

        students = Student.query.filter_by(byclass=request.json.get("class")).all()
    else:
        if Class.query.filter_by(id=request.json.get("class")).first().byuser == user.id:
            students = Student.query.filter_by(byclass=request.json.get("class")).all()
        else:
            return {"code":400,"msg":"你不是该班级的教师"}
    print(students)
    return {"code":200,"msg":"ok","data":[{"id":s.id,"name":s.name,"cid":s.cid} for s in students]}

# Student Mange
@bp.route("/add_student",methods=['POST'])
@token_required
def add_student(user):
    if Student.query.filter_by(cid=request.json.get("cid"),byclass=request.json.get("class")).first():
        return {"code":400,"msg":"学生已存在"}
    if (user.role == Role.query.filter_by(name="Admin").first().id):
        new_student = Student(request.json.get("name"),request.json.get("class"),request.json.get("cid"))
    else:
        if Class.query.filter_by(id=request.json.get("class")).first().byuser == user.id:
             new_student = Student(request.json.get("name"),request.json.get("class"),request.json.get("cid"))
        else:
            return {"code":400,"msg":"你不是该班级的教师"}
    db.session.add(new_student)
    db.session.commit()
    return {"code":200,"msg":"ok"}
