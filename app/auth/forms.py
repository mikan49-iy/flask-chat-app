from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

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

class PasswordChangeForm(FlaskForm):
    password = PasswordField(
        '現在のパスワード',
        validators=[
            DataRequired('現在のパスワードは必須です'),
            Length(
                min=8,
                max=72,
                message="パスワードは8〜72文字で入力してください。"
            )
        ],
    )
    new_password = PasswordField(
        '新しいパスワード',
        validators=[
            DataRequired('新しいパスワードは必須です'),
            Length(
                min=8,
                max=72,
                message="パスワードは8〜72文字で入力してください。"
            )
        ],
    )
    new_password_confirm = PasswordField(
        '新しいパスワード（確認）',
        validators=[
            DataRequired('確認用パスワードは必須です'),
            EqualTo('new_password',
                    message='パスワードが一致していません'
            ),
        ],
    )
    submit = SubmitField('パスワード変更')