from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import SQLAlchemyError

from . import auth_bp
from .forms import LoginForm, PasswordChangeForm
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

        if user.must_change_password:
            return redirect(url_for('auth.password_change'))
        
        if user.role == 'admin':
            return redirect(url_for('admin.user_list'))
        
        if user.role == 'user':
            return redirect(url_for('chat.chat_list'))

        logout_user()
        abort(403)

    return render_template(
        'auth/login.html',
        form=form,
    )

@auth_bp.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route("/password/change", methods=['GET', 'POST'])
@login_required
def password_change():
    form = PasswordChangeForm()

    if form.validate_on_submit():
        current_password = form.password.data

        if not check_password_hash(
            current_user.password_hash,
            current_password,
        ):

            flash(
                '現在のパスワードが正しくありません'
            )
            return render_template(
                'auth/password_change.html',
                form=form,
            )
        
        current_user.password_hash = generate_password_hash(
                form.new_password.data
            )
        
        current_user.must_change_password=False

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('パスワードの変更に失敗しました')
            return render_template(
                'auth/password_change.html',
                form=form,
            )
        flash('パスワードを変更しました')
        
        return redirect(url_for('chat.chat_list'))

    return render_template(
        'auth/password_change.html',
        form=form,
    )