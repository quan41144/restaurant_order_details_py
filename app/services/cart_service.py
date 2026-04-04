from app.models.cart_model import CartModel
from app.services.table_service import TableService

class CartService:
    def __init__(self, db):
        """
        Khởi tạo CartService với kết nối database.
        :param db: Đối tượng Database từ app/database/db.py
        """
        self.db = db
        self.cart_model = CartModel(db)
        # Khởi tạo TableService để cập nhật trạng thái bàn (Màu sắc)
        self.table_service = TableService(db)

    def add_to_cart(self, table_id, item_id, quantity):
        """
        Thêm hoặc bớt số lượng món ăn.
        Sau đó tự động cập nhật trạng thái bàn dựa trên giỏ hàng còn hay hết.
        """
        try:
            # 1. Gọi model để xử lý logic DB (tăng/giảm/xóa)
            self.cart_model.add_item(table_id, item_id, quantity)
            
            # 2. Kiểm tra lại giỏ hàng để cập nhật màu sắc bàn
            self.sync_table_status(table_id)
            
        except Exception as e:
            print(f"Lỗi trong CartService.add_to_cart: {e}")
            raise e

    def get_cart_items(self, table_id):
        """Lấy danh sách món ăn để hiển thị (dùng cho CheckoutScreen)"""
        return self.cart_model.get_items_detail(table_id)

    def remove_from_cart(self, table_id, item_id):
        """Xóa hẳn một món khỏi giỏ hàng"""
        self.cart_model.remove_item(table_id, item_id)
        self.sync_table_status(table_id)

    def sync_table_status(self, table_id):
        """
        Hàm nội bộ để đồng bộ màu sắc bàn:
        - Nếu giỏ có món -> Chuyển sang 'occupied' (Đỏ)
        - Nếu giỏ trống -> Chuyển sang 'empty' (Xanh)
        """
        remaining_items = self.cart_model.get_items(table_id)
        if not remaining_items:
            self.table_service.update_table_status(table_id, 'empty')
        else:
            self.table_service.update_table_status(table_id, 'occupied')

    def checkout(self, table_id):
        """
        Xử lý thanh toán: Xóa giỏ hàng và trả bàn về trạng thái trống.
        """
        try:
            self.cart_model.clear_cart(table_id)
            self.table_service.update_table_status(table_id, 'empty')
            return True
        except Exception as e:
            print(f"Lỗi thanh toán: {e}")
            return False