from flask import render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from . import chat_bp
from ..decorators import user_required
from ..extensions import db
from ..models import Conversation, ConversationMember, Message
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
            .order_by(Message.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

        chat_items.append(
            {
                "conversation": conversation,
                "other_user": other_member.user,
                "latest_message": latest_message,
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

@chat_bp.route("/chats/<int:conversation_id>", methods=["GET", "POST"])
@login_required
@user_required
def chat_room(conversation_id):

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

    messages = db.session.execute(
            db.select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.asc())
        ).scalars().all()

    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            conversation_id = conversation.id,
            sender_id = current_user.id,
            text = form.message.data,
        )

        try:
            db.session.add(message)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('メッセージの送信に失敗しました')
            return render_template(
                'chat/chat_room.html',
                conversation=conversation,
                messages=messages,
                other_user=other_user,
                form=form,
            )
        
        return redirect(url_for('chat.chat_room',conversation_id=conversation.id))

    return render_template(
        'chat/chat_room.html',
        conversation=conversation,
        messages=messages,
        other_user=other_user,
        form = form,
    )