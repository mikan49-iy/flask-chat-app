from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class UserCreateForm(FlaskForm):
    name = StringField(
        '氏名',
        validators=[
            DataRequired('氏名は必須です'),
            Length(
                max=50,
                message="氏名は50文字以内で入力してください。"
            )
        ],
    )
    department = StringField(
        '所属（任意）',
        validators=[
            Optional(),
            Length(
                max=100,
                message="所属は100文字以内で入力してください。"
            )
        ],
    )
    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired('メールアドレスは必須です'),
            Email(message='正しい形式で入力してください'),
            Length(
                max=255,
                message='メールアドレスは255文字以内で入力してください',
            ),
        ],
    )
    password = PasswordField(
        '初期パスワード',
        validators=[
            DataRequired('パスワードは必須です'),
            Length(
                min=8,
                max=72,
                message="パスワードは8〜72文字で入力してください。"
            )
        ],
    )
    password_confirm = PasswordField(
        '初期パスワード（確認）',
        validators=[
            DataRequired('確認用パスワードは必須です'),
            EqualTo('password',
                    message='パスワードが一致していません'
            ),
        ],
    )
    submit = SubmitField('登録')


class UserEditForm(FlaskForm):
    name = StringField(
        '氏名',
        validators=[
            DataRequired('氏名は必須です'),
            Length(
                max=50,
                message="氏名は50文字以内で入力してください。"
            )
        ],
    )
    department = StringField(
        '所属（任意）',
        validators=[
            Optional(),
            Length(
                max=100,
                message="所属は100文字以内で入力してください。"
            )
        ],
    )
    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired('メールアドレスは必須です'),
            Email(message='正しい形式で入力してください'),
            Length(
                max=255,
                message='メールアドレスは255文字以内で入力してください',
            ),
        ],
    )
    
    submit = SubmitField('更新')

class ActionForm(FlaskForm):
    pass

class TemporaryPasswordForm(FlaskForm):

    password = PasswordField(
        '一時パスワード',
        validators=[
            DataRequired('パスワードは必須です'),
            Length(
                min=8,
                max=72,
                message="パスワードは8〜72文字で入力してください。"
            )
        ],
    )
    password_confirm = PasswordField(
        '一時パスワード（確認）',
        validators=[
            DataRequired(
                message='確認用パスワードは必須です'),
            EqualTo('password',
                    message='パスワードが一致していません'
            ),
        ],
    )
    submit = SubmitField('設定')
