import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.table_service import TableService

class MenuScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.image_refs = []      # Giữ tham chiếu ảnh
        self.current_table_id = None 
        
        # Khởi tạo Services
        self.menu_service = MenuService(db)
        self.cart_service = CartService(db)
        self.table_service = TableService(db)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Thực Đơn Nhà Hàng")
        self.resize(900, 750)
        
        main_layout = QVBoxLayout(self)
        
        header = QLabel("MENU PHỤC VỤ")
        header.setFont(QFont("Arial", 22, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; margin: 15px 0;")
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(12)

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        for item in self.menu_service.get_all_menu():
            item_id, name, price, category, raw_path = item
            self.content_layout.addWidget(self.create_item_card(item_id, name, price, category, raw_path, root))

        self.content_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def create_item_card(self, i_id, name, price, cat, raw_path, root):
        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: white; border: 1px solid #eee; border-radius: 12px; }
            QFrame:hover { border: 1px solid #3498db; }
        """)
        layout = QHBoxLayout(card)

        # --- Ảnh ---
        img_lbl = QLabel()
        img_lbl.setFixedSize(140, 110)
        pixmap = QPixmap(140, 110)
        pixmap.fill(Qt.lightGray)

        if raw_path:
            path = raw_path.replace('/', os.sep).replace('\\', os.sep)
            full_path = os.path.join(root, path)
            if not os.path.exists(full_path):
                full_path = os.path.join(root, path.replace('images', 'img'))
            
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path).scaled(140, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        img_lbl.setPixmap(pixmap)
        self.image_refs.append(pixmap)
        layout.addWidget(img_lbl)

        # --- Thông tin ---
        info = QVBoxLayout()
        info.addWidget(QLabel(name, font=QFont("Arial", 13, QFont.Bold)))
        info.addWidget(QLabel(f"{float(price):,.0f} VNĐ", styleSheet="color: #e74c3c; font-weight: bold;"))
        layout.addLayout(info)
        layout.addStretch()

        # --- Cụm nút Tăng (+) / Giảm (-) ---
        qty_layout = QHBoxLayout()
        
        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(40, 40)
        btn_minus.setStyleSheet("background-color: #e74c3c; color: white; font-size: 18px; border-radius: 20px;")
        btn_minus.clicked.connect(lambda _, i=i_id: self.update_qty(i, -1)) # Giảm 1
        
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(40, 40)
        btn_plus.setStyleSheet("background-color: #27ae60; color: white; font-size: 18px; border-radius: 20px;")
        btn_plus.clicked.connect(lambda _, i=i_id: self.update_qty(i, 1))   # Tăng 1

        qty_layout.addWidget(btn_minus)
        qty_layout.addWidget(btn_plus)
        layout.addLayout(qty_layout)

        return card

    # --- ĐÂY LÀ HÀM BỊ THIẾU DẪN ĐẾN LỖI ---
    def update_qty(self, item_id, amount):
        """Hàm xử lý tăng/giảm số lượng"""
        if not self.current_table_id:
            QMessageBox.warning(self, "Lưu ý", "Vui lòng chọn bàn trước!")
            return
        
        try:
            # 1. Gọi service để cập nhật DB (Cộng thêm 'amount' vào số lượng hiện tại)
            self.cart_service.add_to_cart(self.current_table_id, item_id, amount)
            
            # 2. Cập nhật trạng thái màu sắc của bàn
            # Lấy danh sách món hiện tại của bàn
            items = self.cart_service.get_cart_items(self.current_table_id)
            
            if not items:
                # Nếu không còn món nào (giảm hết về 0), đổi bàn sang màu xanh (Trống)
                self.table_service.update_table_status(self.current_table_id, 'empty')
                print(f"Bàn {self.current_table_id} hiện đã trống.")
            else:
                # Nếu vẫn còn món, đảm bảo bàn là màu đỏ (Đang phục vụ)
                self.table_service.update_table_status(self.current_table_id, 'occupied')
                print(f"Cập nhật món ID {item_id} (Lượng: {amount}) cho bàn {self.current_table_id}")

            # 3. Thông báo nhanh
            msg = "Đã thêm món" if amount > 0 else "Đã giảm món"
            self.setWindowTitle(f"Thực Đơn - {msg} thành công!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật: {e}")