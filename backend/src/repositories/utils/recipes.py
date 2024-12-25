from backend.src.constants import MAIN_URL


def recipes_url_paginator(page, limit, count):
    url = f"{MAIN_URL}/api/recipes/"
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
    if (page - 1) * limit > count:  # нужно проверить как работает на фронте
        previous = None
    return {"next": next, "previous": previous}
