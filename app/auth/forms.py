from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired('メールアドレスは必須です'),
            Email(message='正しい形式で入力してください'),
        ],
    )
    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired('パスワードは必須です'),
        ],
    )
    submit = SubmitField('ログイン')