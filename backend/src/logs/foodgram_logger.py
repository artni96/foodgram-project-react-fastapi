from backend.src.schemas.users import UserReadWithRole


def api_success_log(user: UserReadWithRole, request):
    if user:
        return f"Пользователь: {user.email}, запрос: {request}"
    return f"Аноним, запрос: {request}"


def api_exception_log(user: UserReadWithRole | None, request, ex):
    if user:
        return f"При запросе {request} пользователем {user.email} возникла ошибка: {ex}"
    return f"При запросе {request} неаутентифицированным пользователем возникла ошибка: {ex}"
