import os

from backend.src.utils.pdf_shopping_list import create_shopping_list

async def test_create_shopping_list():
    data =  ('абрикос - 100 г', 'яблоко - 200 г', 'банан - 300 г')
    username = 'artni-test'

    shopping_list_pdf = create_shopping_list(data=data, username=username)
    assert os.path.exists(shopping_list_pdf)
    os.remove(shopping_list_pdf)
    assert not os.path.exists(shopping_list_pdf)
