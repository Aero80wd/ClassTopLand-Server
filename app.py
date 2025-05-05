from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from models import *
from views import bp,mail
from userviews import userviews
import os
import uuid
from flask_bootstrap import Bootstrap5
from export_api import yuexun,export_api
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'main.db')
app.config["SECRET_KEY"] = uuid.uuid4().hex
bootstrap = Bootstrap5(app)
app.config['MAIL_SERVER']='smtp.126.com'
app.config['MAIL_PORT'] = 465
app.config["MAIL_USE_SSL"] = True
#app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "Aero8mCapchaBot@126.com"
app.config["MAIL_PASSWORD"] = "RDWKPK9RLgGxuKkS"
app.config["MAIL_SENDER"] = "Aero8mCapchaBot<Aero8mCapchaBot@126.com>"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
mail.init_app(app)
app.register_blueprint(bp)
app.register_blueprint(userviews,url_prefix="/web/v1")
app.register_blueprint(yuexun,url_prefix="/exapi/yuexun")
app.register_blueprint(export_api,url_prefix="/exapi")
print("""   ____  _                  _____              _                       _ 
  / ___|| |  __ _  ___  ___|_   _|___   _ __  | |     __ _  _ __    __| |
 | |    | | / _` |/ __|/ __| | | / _ \ | '_ \ | |    / _` || '_ \  / _` |
 | |___ | || (_| |\__ \\__ \ | || (_) || |_) || |___| (_| || | | || (_| |
  \____||_| \__,_||___/|___/ |_| \___/ | .__/ |_____|\__,_||_| |_| \__,_|
                                       |_|                               
                            Powered By Aero8m""")
if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=8765)
