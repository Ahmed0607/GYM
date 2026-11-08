from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

TIME_OFFSET = timedelta(seconds=0)
MOCK_ENABLED = True
CAIRO_TZ = ZoneInfo("Africa/Cairo")

def get_current_time():
    if not MOCK_ENABLED:
        return datetime.now(CAIRO_TZ)
    return datetime.now(timezone.utc) + TIME_OFFSET

def set_time_offset(target_date: datetime):
    global TIME_OFFSET
    TIME_OFFSET = target_date - datetime.now(timezone.utc)

def set_mock_enabled(enabled: bool):
    global MOCK_ENABLED
    MOCK_ENABLED = enabled
    
def is_mock_enabled():
    return MOCK_ENABLED
