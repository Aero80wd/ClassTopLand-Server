from flask import Blueprint,render_template,flash,redirect,url_for
from models import db,User,Class,Role,Student
from form import ConfirmForm,ConfirmRedirectForm
import uuid

userviews = Blueprint('userviews',__name__)
@userviews.route("/confirm_redirect/<token>",methods=["GET","POST"])
def confirm_redirect(token):
    form = ConfirmRedirectForm()
    if form.validate_on_submit():
        return redirect(url_for("userviews.confirm",token=token))
    return render_template("user_confirm_redirect.html",form=form)
@userviews.route("/confirm/<token>",methods=["GET","POST"])
def confirm(token):
    if token[0] == "b" and token[1] =="'" and token[-1] == "'":
        token = token[2:-1]
    print(token)
    user = User.verify_confirm_token(token)
    if user:
        form = ConfirmForm()
        confirm_string = uuid.uuid4().hex
        if form.validate_on_submit():
            user.iscomfirm = True
            db.session.commit()
            flash("账户已确认成功")
            return redirect(url_for("userviews.confirm_ok"))
        
        return render_template("user_comfirm.html",user=user,form=form,confirm_string=confirm_string)
    else:
        return render_template("user_comfirm_404.html")

@userviews.route("/confirm_ok")
def confirm_ok():
    return render_template("user_confirm_ok.html")