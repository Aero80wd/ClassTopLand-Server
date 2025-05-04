from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from authlib.jose import jwt, JoseError
import hashlib
import secrets
db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    def __init__(self,name):
        self.name = name
    @staticmethod
    def create_role():
        admin = Role("Admin")
        user = Role("User")
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(64))
    token = db.Column(db.String(64))
    qq = db.Column(db.String(100))
    role = db.Column(db.Integer,db.ForeignKey('role.id'))
    iscomfirm = db.Column(db.Boolean)
    def __init__(self,name,password,role,qq):
        self.name = name
        h = hashlib.sha256()
        h.update(password.encode('utf-8'))
        self.password = h.hexdigest()
        self.token = secrets.token_hex(32)
        self.role = role
        self.qq = qq
    def generate_confirm_token(self):
        header = {'alg': 'HS256'}
        # 用于签名的密钥
        key = current_app.config['SECRET_KEY']
        data = {"user_id": self.id}
        token = jwt.encode(header, data, key)
        return str(token)
    @staticmethod
    def verify_confirm_token(token):
        key = current_app.config['SECRET_KEY']
        try:
            data = jwt.decode(token, key)
            user_id = data['user_id']
            user = User.query.get(user_id)
            return user
        except JoseError:
            return None
    def __repr__(self):
        return f'<User {self.name}>'

class Class(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    byuser = db.Column(db.Integer,db.ForeignKey('user.id'))
    def __init__(self,name,byuser):
        self.name = name
        self.byuser = byuser
    def __repr__(self):
        return f'<Class {self.name}>'
class Student(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    byclass = db.Column(db.Integer,db.ForeignKey('class.id'))
    cid = db.Column(db.Integer)
    def __init__(self,name,byclass,cid):
        self.name = name
        self.byclass = byclass
        self.cid = cid
    def __repr__(self):
        return f'<Student {self.name}>'