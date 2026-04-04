class OrderModel:
    def __init__(self, db):
        self.db = db

    def create_order(self, table_id):
        query = "INSERT INTO orders(table_id) VALUES (%s) RETURNING id"
        return self.db.fetch_one(query, (table_id,))