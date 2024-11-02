from backend.src.constants import MAIN_URL


async def subs_url_paginator(page, limit, count):
    url = f'{MAIN_URL}/subscriptions'
    next, previous = None, None
    if not page:
        page = 1
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
