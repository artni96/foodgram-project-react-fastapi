from argon2 import PasswordHasher
from backend.src.constants import MAIN_URL


class PasswordManager:
    ph = PasswordHasher()

    def hash_password(self, password):
        return self.ph.hash(password)

    def verify_password(self, hashed_password, current_password):
        return self.ph.verify(hashed_password, current_password)


async def users_url_paginator(page, limit, count):
    url = f'{MAIN_URL}/users'
    next, previous = None, None
    if not page:
        page = 1
    else:
        page += 1
    if page * limit < count:
        next = url + f'?page={page+1}&limit={limit}'
    if page != 1:
        if page == 2:
            previous = url + f'?limit={limit}'
        else:
            previous = url + f'?page={page-1}&limit={limit}'
    return {
        'next': next,
        'previous': previous
    }