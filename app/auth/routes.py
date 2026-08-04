from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from . import auth_bp
from .forms import LoginForm
from ..extensions import db
from ..models import User

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if not user or not check_password_hash(
            user.password_hash,
            password,
        ):

            flash(
                'メールアドレスまたはパスワードが正しくありません'
            )
            return render_template(
                'auth/login.html',
                form=form,
            )
        
        if not user.is_active:
            flash('このアカウントは現在使用できません')
            return render_template(
                'auth/login.html',
                form=form,
            )

        login_user(user)

        return redirect(url_for('index'))

    return render_template(
        'auth/login.html',
        form=form,
    )

@auth_bp.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))