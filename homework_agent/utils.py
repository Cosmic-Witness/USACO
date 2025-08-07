from datetime import datetime


def parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except Exception:
        return False