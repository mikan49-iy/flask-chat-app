from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):

    message = TextAreaField(
        "メッセージ",
        validators=[
            DataRequired("メッセージを入力してください。"),
            Length(
                max=500,
                message="メッセージは500文字以内で入力してください。"
            )
        ],
    )
    submit = SubmitField('送信')