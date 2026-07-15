import click
from flask.cli import with_appcontext
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import User


@click.command("create-admin")
@click.option("--name", prompt="管理者名")
@click.option("--email", prompt="メールアドレス")
@click.option(
    "--password",
    prompt="パスワード",
    hide_input=True,
    confirmation_prompt=True,
)
@with_appcontext
def create_admin(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name:
        raise click.ClickException("管理者名を入力してください。")

    if not email:
        raise click.ClickException("メールアドレスを入力してください。")

    if len(password) < 8:
        raise click.ClickException(
            "パスワードは8文字以上で入力してください。"
        )

    existing_user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        raise click.ClickException(
            "このメールアドレスは既に使用されています。"
        )

    admin = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
        is_active=True,
        must_change_password=False,
    )

    try:
        db.session.add(admin)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        raise click.ClickException(
            "管理者アカウントの保存に失敗しました。"
        ) from error

    click.echo("管理者アカウントを作成しました。")