from datetime import timezone
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")


def to_jst(dt):
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(JST)