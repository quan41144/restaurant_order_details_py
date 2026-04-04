class CartModel:
    def __init__(self, db):
        """
        Khởi tạo Model quản lý giỏ hàng.
        :param db: Đối tượng kết nối Database từ app/database/db.py
        """
        self.db = db

    def add_item(self, table_id, item_id, quantity):
        """
        Thêm hoặc cập nhật số lượng món ăn trong giỏ hàng.
        - Nếu quantity > 0: Tăng số lượng.
        - Nếu quantity < 0: Giảm số lượng.
        - Nếu tổng số lượng sau cập nhật <= 0: Xóa món khỏi giỏ hàng.
        """
        # 1. Tìm ID giỏ hàng (cart) của bàn hiện tại
        cart = self.db.fetch_one(
            "SELECT id FROM carts WHERE table_id = %s",
            (table_id,)
        )

        # 2. Nếu bàn chưa có giỏ hàng, tạo mới (chỉ khi quantity > 0)
        if not cart:
            if quantity <= 0:
                return # Không thể giảm món khi chưa có giỏ hàng
            cart = self.db.fetch_one(
                "INSERT INTO carts(table_id) VALUES (%s) RETURNING id",
                (table_id,)
            )
        
        cart_id = cart[0]

        # 3. Kiểm tra xem món ăn này đã có trong giỏ hàng của bàn này chưa
        existing_item = self.db.fetch_one(
            "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND menu_item_id = %s",
            (cart_id, item_id)
        )

        if existing_item:
            item_entry_id = existing_item[0]
            current_qty = existing_item[1]
            new_qty = current_qty + quantity # Thực hiện cộng/trừ số lượng

            if new_qty > 0:
                # Cập nhật số lượng mới nếu vẫn còn ít nhất 1 món
                query = "UPDATE cart_items SET quantity = %s WHERE id = %s"
                self.db.execute(query, (new_qty, item_entry_id))
            else:
                # Xóa món khỏi giỏ hàng nếu số lượng về 0 hoặc âm
                query = "DELETE FROM cart_items WHERE id = %s"
                self.db.execute(query, (item_entry_id,))
                
        elif quantity > 0:
            # Nếu món chưa có và hành động là thêm mới (quantity > 0)
            query = """
            INSERT INTO cart_items(cart_id, menu_item_id, quantity)
            VALUES (%s, %s, %s)
            """
            self.db.execute(query, (cart_id, item_id, quantity))

    def get_items(self, table_id):
        """
        Lấy danh sách thô các món ăn trong giỏ hàng của một bàn (dùng để kiểm tra trạng thái bàn).
        """
        query = """
        SELECT ci.* 
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        WHERE c.table_id = %s
        """
        return self.db.fetch_all(query, (table_id,))

    def get_items_detail(self, table_id):
        """
        Lấy danh sách món ăn chi tiết (Tên, Giá, SL, Tổng tiền) để hiển thị lên màn hình Thanh toán.
        Trả về 5 cột: (Tên món, Giá, Số lượng, Tổng tiền món, ID món ăn)
        """
        query = """
        SELECT 
            mi.name, 
            mi.price, 
            ci.quantity, 
            (mi.price * ci.quantity) as total, 
            mi.id
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        JOIN menu_items mi ON ci.menu_item_id = mi.id
        WHERE c.table_id = %s
        ORDER BY mi.name ASC
        """
        return self.db.fetch_all(query, (table_id,))

    def remove_item(self, table_id, menu_item_id):
        """
        Xóa hoàn toàn một món ăn khỏi giỏ hàng của bàn (không quan tâm số lượng).
        """
        query = """
        DELETE FROM cart_items 
        WHERE menu_item_id = %s 
        AND cart_id IN (SELECT id FROM carts WHERE table_id = %s)
        """
        self.db.execute(query, (menu_item_id, table_id))

    def clear_cart(self, table_id):
        """
        Xóa toàn bộ giỏ hàng của một bàn (thường gọi sau khi thanh toán thành công).
        """
        query = "DELETE FROM carts WHERE table_id = %s"
        self.db.execute(query, (table_id,))