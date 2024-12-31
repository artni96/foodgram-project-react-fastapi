from passlib.context import CryptContext

from backend.src.config import settings
import jwt

from backend.src.exceptions.users import IncorrectTokenException, ExpiredTokenException


class PasswordManager:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)



def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.exceptions.DecodeError:
        raise IncorrectTokenException
    except jwt.exceptions.ExpiredSignatureError:
        raise ExpiredTokenException
