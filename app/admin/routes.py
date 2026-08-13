from flask import render_template, flash, redirect, url_for, abort
from flask_login import login_required
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError

from . import admin_bp
from ..decorators import admin_required
from ..extensions import db
from ..models import User
from .forms import UserCreateForm, UserEditForm, TemporaryPasswordForm
from ..forms import ActionForm

@admin_bp.route("/users", methods=['GET'])
@login_required
@admin_required
def user_list():
    active_users = db.session.execute(
        db.select(User)
        .where(
            User.role == 'user',
            User.is_active.is_(True),
        )
        .order_by(User.name)
    ).scalars().all()

    inactive_users = db.session.execute(
        db.select(User)
        .where(
            User.role == 'user',
            User.is_active.is_(False),
        )
        .order_by(User.name)
    ).scalars().all()

    action_form = ActionForm()

    return render_template(
        'admin/user_list.html',
        active_users=active_users,
        inactive_users=inactive_users,
        action_form=action_form,
    )

@admin_bp.route("/users/new", methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserCreateForm()

    if form.validate_on_submit():
        name = form.name.data.strip()

        department = form.department.data.strip()
        if department == "":
            department = None
        
        email = form.email.data.strip().lower()
        
        existing_user = db.session.execute(
            db.select(User).where(User.email==email)
        ).scalar_one_or_none()
            
        if existing_user:
            flash("このメールアドレスは既に使用されています")
            return render_template(
                "admin/user_create.html",
                form=form,
            )

        user = User(
            name=name,
            department=department,
            email=email,
            password_hash=generate_password_hash(
                form.password.data
            ),
        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('ユーザーの登録に失敗しました')
            return render_template(
                'admin/user_create.html',
                form=form,
            )
        flash('ユーザーを登録しました')
        return redirect(url_for('admin.user_list'))

    return render_template(
        'admin/user_create.html',
        form=form,
    )

@admin_bp.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.role != 'user':
        abort(404)

    form = UserEditForm(obj=user)

    if form.validate_on_submit():

        name = form.name.data.strip()

        department = form.department.data.strip()
        if department == "":
            department = None

        email = form.email.data.strip().lower()

        existing_user = db.session.execute(
            db.select(User).where(
                User.email == email,
                User.id != user.id
            )
        ).scalar_one_or_none()
            
        if existing_user:
            flash("このメールアドレスは既に使用されています")
            return render_template(
                "admin/user_edit.html",
                form=form,
            )

        user.name = name
        user.department = department
        user.email = email

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('ユーザー情報の編集に失敗しました')
            return render_template(
                'admin/user_edit.html',
                form=form,
            )
        flash('ユーザー情報を編集しました')
        return redirect(url_for('admin.user_list'))
    
    return render_template(
        'admin/user_edit.html',
        form=form,
    )

@admin_bp.route("/users/<int:user_id>/deactivate", methods=['POST'])
@login_required
@admin_required
def user_deactivate(user_id):
    form = ActionForm()

    if not form.validate_on_submit():
        abort(404)

    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.role != 'user':
        abort(404)

    user.is_active = False

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash('ユーザーの無効化に失敗しました')
        return redirect(url_for('admin.user_list'))
    
    flash("ユーザーを無効化しました。")
    return redirect(url_for('admin.user_list'))

@admin_bp.route("/users/<int:user_id>/activate", methods=['POST'])
@login_required
@admin_required
def user_activate(user_id):
    form = ActionForm()

    if not form.validate_on_submit():
        abort(404)

    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.role != 'user':
        abort(404)

    user.is_active = True

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash('ユーザーの有効化に失敗しました')
        return redirect(url_for('admin.user_list'))
    
    flash("ユーザーを有効化しました。")
    return redirect(url_for('admin.user_list'))

@admin_bp.route("/users/<int:user_id>/temporary-password", methods=['GET','POST'])
@login_required
@admin_required
def temporary_password_set(user_id):
    
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.role != "user":
        abort(404)

    form = TemporaryPasswordForm()

    if form.validate_on_submit():
        user.password_hash=generate_password_hash(
                form.password.data
        )

        user.must_change_password = True

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('一時パスワードの設定に失敗しました')
            return redirect(
                url_for(
                    'admin.temporary_password_set',
                    user_id=user.id,
                )
            )
        flash('一時パスワードを設定しました')
        return redirect(url_for('admin.user_list'))

    return render_template(
        'admin/temporary_password.html',
        form=form,
        user=user,
    )