class OrderService:
    def __init__(self, db):
        self.db = db

    def process_checkout(self, table_id):
        # 1. Tạo Order mới
        order_query = "INSERT INTO orders (table_id, status) VALUES (%s, 'pending') RETURNING id"
        order_id = self.db.fetch_one(order_query, (table_id,))[0]

        # 2. Chuyển món từ giỏ hàng sang chi tiết hóa đơn (order_items)
        move_items_query = """
        INSERT INTO order_items (order_id, menu_item_id, quantity)
        SELECT %s, menu_item_id, quantity 
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        WHERE c.table_id = %s
        """
        self.db.execute(move_items_query, (order_id, table_id))

        # 3. Tính tổng tiền để tạo bản ghi Payment
        sum_query = """
        SELECT SUM(mi.price * ci.quantity) 
        FROM cart_items ci 
        JOIN menu_items mi ON ci.menu_item_id = mi.id
        JOIN carts c ON ci.cart_id = c.id
        WHERE c.table_id = %s
        """
        total_amount = self.db.fetch_one(sum_query, (table_id,))[0]

        # 4. Tạo Payment
        self.db.execute(
            "INSERT INTO payments (order_id, total_amount, status) VALUES (%s, %s, 'unpaid')",
            (order_id, total_amount)
        )

        # 5. Xóa giỏ hàng và Cập nhật trạng thái bàn thành 'empty'
        self.db.execute("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE table_id = %s)", (table_id,))
        self.db.execute("UPDATE order_tables SET status = 'empty' WHERE id = %s", (table_id,))
        
        return order_id, total_amount