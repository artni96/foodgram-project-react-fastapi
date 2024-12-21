from starlette.requests import Request

from backend.src.schemas.users import UserReadWithRole


def api_logger(user: UserReadWithRole, request: Request, status_code: int):
    if user:
        return f'Пользователь: {user.email}, запрос: {request}, статус ответа: {status_code}'
    return f'Аноним, запрос: {request}, статус ответа: {status_code}'
