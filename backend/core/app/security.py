from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError


def create_access_token(data: dict, secret: str, expires_minutes: int) -> str:
    to_encode = dict(data)
    exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, secret, algorithm="HS256")


def decode_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        return {}