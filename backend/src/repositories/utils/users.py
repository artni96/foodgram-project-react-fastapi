from passlib.context import CryptContext

from backend.src.config import settings
from backend.src.constants import MAIN_URL
import jwt

from backend.src.exceptions.users import IncorrectTokenException, ExpiredTokenException


class PasswordManager:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)


async def users_url_paginator(page, limit, count):
    url = f"{MAIN_URL}/api/users"
    next, previous = None, None
    if not page:
        page = 1
    if page * limit < count:
        next = url + f"?page={page+1}&limit={limit}"
    if page != 1:
        if page == 2:
            previous = url + f"?limit={limit}"
        else:
            previous = url + f"?page={page-1}&limit={limit}"
    return {"next": next, "previous": previous}


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.exceptions.DecodeError:
        raise IncorrectTokenException
    except jwt.exceptions.ExpiredSignatureError:
        raise ExpiredTokenException
