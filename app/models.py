from datetime import datetime, timezone
from .extensions import db

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    department = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    conversation_members = db.relationship("ConversationMember", back_populates="user", lazy=True)
    sent_messages = db.relationship("Message", back_populates="sender", lazy=True)

class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    members = db.relationship("ConversationMember", back_populates="conversation", lazy=True)
    messages = db.relationship("Message", back_populates="conversation", lazy=True)

class ConversationMember(db.Model):
    __tablename__ = "conversation_members"

    __table_args__ = (
        db.UniqueConstraint("conversation_id", "user_id", name="uq_conversation_member",),
    )

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_read_message_id = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=True)

    conversation = db.relationship("Conversation", back_populates="members")
    user = db.relationship("User", back_populates="conversation_members")
    last_read_message = db.relationship("Message", back_populates="read_by_members")

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    conversation = db.relationship("Conversation", back_populates="messages")
    sender = db.relationship("User", back_populates="sent_messages")
    read_by_members = db.relationship("ConversationMember", back_populates="last_read_message", lazy=True)