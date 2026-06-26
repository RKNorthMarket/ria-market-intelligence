from datetime import datetime


def timestamp():
    return datetime.utcnow().isoformat()
