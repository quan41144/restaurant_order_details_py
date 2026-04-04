class MenuService:
    def __init__(self, db):
        self.db = db

    def get_all_menu(self):
        query = "SELECT id, name, price, category, image FROM menu_items"
        return self.db.fetch_all(query)