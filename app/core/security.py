from datetime import datetime, timedelta
from typing import Optional, Dict
import bcrypt
from jose import jwt, JWTError

SECRET_KEY = "CHANGE-ME"                     # move to env var in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or
                                  timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# -----------------------------------------------------------------
# legacy aliases so old imports keep working
decode_token = decode_access_token
hash_password = get_password_hash
# -----------------------------------------------------------------
