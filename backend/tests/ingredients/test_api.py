from backend.src.config import settings

def test_first(check_test_mode):
    print(settings.DB_NAME)
    assert 1 == 1
