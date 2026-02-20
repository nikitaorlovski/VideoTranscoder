import datetime
import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


def encode_jwt(
    payload: dict,
    algorithm: str = settings.auth.algorithm,
    private_key: str = settings.auth.private_key_path.read_text(),
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    expire = now + datetime.timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)
    return jwt.encode(payload=to_encode, algorithm=algorithm, key=private_key)


def decode_jwt(
    token: str,
    algorithm: str = settings.auth.algorithm,
    public_key: str = settings.auth.public_key_path.read_text(),
) -> str:
    return jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])
