def add_to_cart(self, item_id):
        try:
            # Lấy table_id hiện tại (được truyền từ MainWindow)
            table_id = self.current_table_id 
            
            # 1. Thêm món vào giỏ
            self.cart_service.add_to_cart(table_id, item_id, 1)
            
            # 2. CẬP NHẬT TRẠNG THÁI BÀN THÀNH ĐANG PHỤC VỤ
            from app.services.table_service import TableService
            table_service = TableService(self.db)
            table_service.set_table_occupied(table_id)
            
            print(f"Đã thêm món và đổi trạng thái bàn {table_id} sang Occupied")
        except Exception as e:
            print(f"Lỗi: {e}")