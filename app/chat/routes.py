from flask import render_template
from flask_login import login_required, current_user

from . import chat_bp
from ..decorators import user_required
from ..extensions import db
from ..models import ConversationMember, Message


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