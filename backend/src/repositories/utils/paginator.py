from backend.src.constants import MAIN_URL


def url_paginator(page, limit, count, router_prefix):
    url = f"{MAIN_URL}{router_prefix}"
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
    if (page - 1) * limit > count:
        previous = None
    return {"next": next, "previous": previous}
