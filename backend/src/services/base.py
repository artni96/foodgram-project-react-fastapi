from backend.src.db_manager import DBManager


class BaseService:
    db: DBManager | None = None

    def __init__(self, db: DBManager):
        self.db = db
