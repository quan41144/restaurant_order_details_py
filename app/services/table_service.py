class TableService:
    def __init__(self, db):
        self.db = db

    def get_all_tables(self):
        return self.db.fetch_all("SELECT id, name, status FROM order_tables ORDER BY id")

    def update_table_status(self, table_id, status):
        """Hàm quan trọng để đổi màu bàn trong DB"""
        query = "UPDATE order_tables SET status = %s WHERE id = %s"
        self.db.execute(query, (status, table_id))