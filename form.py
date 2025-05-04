from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
class ConfirmRedirectForm(FlaskForm):
    submit = SubmitField("继续访问")
class ConfirmForm(FlaskForm):
    submit = SubmitField('验证')