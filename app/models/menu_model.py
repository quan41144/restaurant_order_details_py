class MenuModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM menu")