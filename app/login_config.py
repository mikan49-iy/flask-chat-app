from .extensions import db, login_manager
from .models import User

login_manager.login_view = "auth.login"
login_manager.login_message = "ログインが必要です"

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None