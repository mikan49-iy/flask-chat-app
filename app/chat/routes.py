from flask import render_template, flash, redirect, url_for, abort, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from . import chat_bp
from ..decorators import user_required
from ..extensions import db
from ..models import  User, Conversation, ConversationMember, Message
from ..utils import to_jst
from .forms import MessageForm

@chat_bp.route("/chats", methods=["GET"])
@login_required
@user_required
def chat_list():
    memberships = db.session.execute(
        db.select(ConversationMember).where(
            ConversationMember.user_id == current_user.id
        )
    ).scalars().all()

    chat_items = []

    for membership in memberships:
        conversation = membership.conversation

        other_member = None

        for member in conversation.members:
            if member.user_id != current_user.id:
                other_member = member
                break

        if other_member is None:
            continue

        latest_message = db.session.execute(
            db.select(Message)
            .where(
                Message.conversation_id == conversation.id
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        latest_message_created_at_jst = None

        if latest_message is not None:
            latest_message_created_at_jst = (
                to_jst(latest_message.created_at)
                .strftime("%Y/%m/%d %H:%M")
            )

        unread = False

        if latest_message is not None:

            if (
                latest_message.sender_id != current_user.id
                and membership.last_read_message_id != latest_message.id
            ):
                unread = True

        chat_items.append(
            {
                "conversation": conversation,
                "other_user": other_member.user,
                "latest_message": latest_message,
                "latest_message_created_at_jst": latest_message_created_at_jst,
                "unread": unread
            }
        )

    def get_sort_datetime(item):
        if item["latest_message"]:
            return item["latest_message"].created_at

        return item["conversation"].created_at

    chat_items.sort(
        key=get_sort_datetime,
        reverse=True,
    )

    return render_template(
        "chat/chat_list.html",
        chat_items=chat_items,
    )

@chat_bp.route("/chats/<int:conversation_id>", methods=["GET"])
@login_required
@user_required
def chat_room(conversation_id):

    conversation = db.session.get(Conversation, conversation_id)

    if conversation is None:
        abort(404)

    conversation_member = None

    for member in conversation.members:
        if member.user_id == current_user.id:
            conversation_member = member
            break

    if conversation_member is None:
        abort(404)

    other_user = None

    for member in conversation.members:
        if member.user_id != current_user.id:
            other_user = member.user
            break

    if other_user is None:
        abort(404)

    messages = db.session.execute(
            db.select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.asc())
        ).scalars().all()

    if messages:
        latest_message = messages[-1]
        conversation_member.last_read_message_id = latest_message.id

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "既読情報の更新に失敗しました。",
                "danger",
            )
    
    form = MessageForm()

    return render_template(
        'chat/chat_room.html',
        conversation=conversation,
        other_user=other_user,
        form=form,
    )

@chat_bp.route("/chats/users", methods=["GET"])
@login_required
@user_required
def user_list():
    users = db.session.execute(
        db.select(User)
        .where(
            User.role == 'user',
            User.is_active.is_(True),
            User.id != current_user.id,
        )
        .order_by(User.name)
    ).scalars().all()

    return render_template(
        'chat/user_list.html',
        users=users,
    )

@chat_bp.route("/chats/users/<int:user_id>/start", methods=["POST"])
@login_required
@user_required
def chat_start(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.role != 'user':
        abort(404)

    if not user.is_active:
        abort(404)
    
    if user.id == current_user.id:
        abort(404)

    my_memberships = db.session.execute(
        db.select(ConversationMember).where(
            ConversationMember.user_id == current_user.id
        )
    ).scalars().all()

    for membership in my_memberships:
        conversation = membership.conversation

        for member in conversation.members:
            if member.user_id == user_id:
                return redirect(
                    url_for(
                    'chat.chat_room',
                    conversation_id=conversation.id,
                    )
                )

    conversation = Conversation()

    try:
        db.session.add(conversation)
        db.session.flush()

        current_user_member = ConversationMember(
            conversation_id=conversation.id,
            user_id=current_user.id,
        )

        other_user_member = ConversationMember(
            conversation_id=conversation.id,
            user_id=user.id,
        )
    
        db.session.add_all(
            [
                current_user_member,
                other_user_member,
            ]
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        flash('チャット画面の作成に失敗しました', 'danger')
        return redirect(url_for("chat.user_list"))
    
    return redirect(
        url_for(
            'chat.chat_room',
            conversation_id=conversation.id,
        )
    )

@chat_bp.route("/chats/<int:conversation_id>/messages", methods=["GET"])
@login_required
@user_required
def get_messages(conversation_id):
    conversation = db.session.get(Conversation, conversation_id)

    if conversation is None:
        abort(404)

    is_member = False
    
    for member in conversation.members:
        if member.user_id == current_user.id:
            is_member = True
            break

    if not is_member:
        abort(404)

    messages = db.session.execute(
            db.select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.asc(), Message.id.asc())
        ).scalars().all()
    
    message_data = []
    
    for message in messages:
        message_data.append(
            {
                "id": message.id,
                "text": message.text,
                "sender_id": message.sender_id,
                "created_at": to_jst(message.created_at).strftime("%Y/%m/%d %H:%M"),
            }            
        )

    return jsonify(message_data)

@chat_bp.route("/chats/<int:conversation_id>/messages", methods=["POST"])
@login_required
@user_required
def send_message(conversation_id):
    conversation = db.session.get(Conversation, conversation_id)

    if conversation is None:
        abort(404)

    is_member = False
    
    for member in conversation.members:
        if member.user_id == current_user.id:
            is_member = True
            break

    if not is_member:
        abort(404)

    other_user = None

    for member in conversation.members:
        if member.user_id != current_user.id:
            other_user = member.user
            break

    if other_user is None:
        abort(404)

    if not other_user.is_active:
        return jsonify(
            {
                "error": "このユーザーには現在メッセージを送信できません。"
            }
        ), 403

    form = MessageForm()

    if not form.validate_on_submit():
        return jsonify(
            {
                "errors": form.errors,
            }
        ), 400
    
    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        text=form.message.data,
    )

    try:
        db.session.add(message)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "error": "メッセージの送信に失敗しました。"
            }
        ), 500
    
    return jsonify(
        {
            "id": message.id,
            "text": message.text,
            "sender_id": message.sender_id,
            "created_at": to_jst(message.created_at).strftime("%Y/%m/%d %H:%M"),
        }
    ), 201

@chat_bp.route("/chats/<int:conversation_id>/read", methods=["POST"])
@login_required
@user_required
def mark_as_read(conversation_id):
    conversation = db.session.get(Conversation, conversation_id)

    if conversation is None:
        abort(404)

    conversation_member = None

    for member in conversation.members:
        if member.user_id == current_user.id:
            conversation_member = member
            break

    if conversation_member is None:
        abort(404)

    data = request.get_json(silent=True)

    if data is None:
        abort(400)

    last_read_message_id = data.get("last_read_message_id")

    if last_read_message_id is None:
        abort(400)

    message = db.session.get(Message, last_read_message_id)

    if message is None:
        abort(400)

    if message.conversation_id != conversation.id:
        abort(400)

    if (
        conversation_member.last_read_message_id is None
        or message.id > conversation_member.last_read_message_id
    ):
        conversation_member.last_read_message_id = message.id

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "error": "既読情報の更新に失敗しました。"
            }
        ), 500
    
    return jsonify(
        {
            "last_read_message_id": message.id,
        }
    ), 200