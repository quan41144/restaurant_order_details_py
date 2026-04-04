import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CheckoutScreen(QWidget):
    def __init__(self, db, table_id):
        super().__init__()
        self.db = db
        self.table_id = table_id
        self.total_amount = 0
        
        # Khởi tạo Service (Đảm bảo các file này đã có self.db)
        from app.services.cart_service import CartService
        self.cart_service = CartService(db)
        
        self.init_ui()
        self.load_cart_items()

    def init_ui(self):
        self.setWindowTitle(f"Thanh toán - Bàn {self.table_id}")
        self.resize(500, 700)
        self.setStyleSheet("background-color: #f4f7f6;")
        
        self.main_layout = QVBoxLayout(self)

        # --- Tiêu đề ---
        header = QLabel(f"CHI TIẾT HÓA ĐƠN BÀN {self.table_id}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        self.main_layout.addWidget(header)

        # --- Khu vực danh sách món ăn (Scroll Area) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.container = QWidget()
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.items_layout.setSpacing(10)
        
        scroll.setWidget(self.container)
        self.main_layout.addWidget(scroll)

        # --- Tổng kết tiền ---
        footer = QFrame()
        footer.setStyleSheet("background-color: white; border-top: 2px solid #ddd;")
        footer_layout = QVBoxLayout(footer)
        
        total_row = QHBoxLayout()
        lbl_total_text = QLabel("TỔNG CỘNG:")
        lbl_total_text.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.lbl_total_all = QLabel("0 VNĐ")
        self.lbl_total_all.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_total_all.setStyleSheet("color: #e74c3c;")
        
        total_row.addWidget(lbl_total_text)
        total_row.addStretch()
        total_row.addWidget(self.lbl_total_all)
        footer_layout.addLayout(total_row)

        # --- Nút Thanh Toán ---
        self.btn_pay = QPushButton("XÁC NHẬN THANH TOÁN")
        self.btn_pay.setFixedHeight(50)
        self.btn_pay.setCursor(Qt.PointingHandCursor)
        self.btn_pay.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.btn_pay.clicked.connect(self.process_payment)
        footer_layout.addWidget(self.btn_pay)

        self.main_layout.addWidget(footer)

    def load_cart_items(self):
        """Xóa danh sách cũ và nạp lại dữ liệu từ Database"""
        # 1. Xóa các widget hiện tại trong layout
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Lấy dữ liệu mới
        items = self.cart_service.get_cart_items(self.table_id)
        self.total_amount = 0

        if not items:
            empty_lbl = QLabel("Giỏ hàng đang trống")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.items_layout.addWidget(empty_lbl)
            self.lbl_total_all.setText("0 VNĐ")
            return

        for item in items:
            # Cấu trúc item: (name, price, quantity, total, menu_item_id)
            name, price, qty, total, m_id = item
            self.total_amount += total

            # Tạo widget cho mỗi dòng món ăn
            row_frame = QFrame()
            row_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
            row_layout = QHBoxLayout(row_frame)

            # Thông tin tên và giá đơn lẻ
            info_lbl = QLabel(f"<b>{name}</b><br><font color='#7f8c8d'>{price:,.0f}đ</font>")
            row_layout.addWidget(info_lbl, 3)

            # --- CỤM NÚT TĂNG/GIẢM ---
            qty_layout = QHBoxLayout()
            
            btn_minus = QPushButton("-")
            btn_minus.setFixedSize(30, 30)
            btn_minus.setStyleSheet("background-color: #ecf0f1; border-radius: 15px; font-weight: bold;")
            btn_minus.clicked.connect(lambda _, i=m_id: self.update_quantity(i, -1))
            
            lbl_qty = QLabel(str(qty))
            lbl_qty.setFixedWidth(25)
            lbl_qty.setAlignment(Qt.AlignCenter)
            lbl_qty.setFont(QFont("Arial", 10, QFont.Bold))
            
            btn_plus = QPushButton("+")
            btn_plus.setFixedSize(30, 30)
            btn_plus.setStyleSheet("background-color: #ecf0f1; border-radius: 15px; font-weight: bold;")
            btn_plus.clicked.connect(lambda _, i=m_id: self.update_quantity(i, 1))

            qty_layout.addWidget(btn_minus)
            qty_layout.addWidget(lbl_qty)
            qty_layout.addWidget(btn_plus)
            row_layout.addLayout(qty_layout, 2)

            # Thành tiền của món
            item_total_lbl = QLabel(f"{total:,.0f}đ")
            item_total_lbl.setFixedWidth(80)
            item_total_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_total_lbl.setStyleSheet("color: #c0392b; font-weight: bold;")
            row_layout.addWidget(item_total_lbl, 2)

            self.items_layout.addWidget(row_frame)

        # Cập nhật tổng tiền cuối cùng
        self.lbl_total_all.setText(f"{self.total_amount:,.0f} VNĐ")

    def update_quantity(self, menu_item_id, amount):
        """Xử lý khi nhấn nút + hoặc -"""
        try:
            # Gọi service để cộng/trừ trong DB
            self.cart_service.add_to_cart(self.table_id, menu_item_id, amount)
            # Nạp lại giao diện để thấy thay đổi
            self.load_cart_items()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật số lượng: {e}")

    def process_payment(self):
        """Xử lý nghiệp vụ thanh toán cuối cùng"""
        if self.total_amount == 0:
            QMessageBox.warning(self, "Lỗi", "Không có món ăn để thanh toán!")
            return

        reply = QMessageBox.question(self, "Xác nhận", 
                                   f"Tổng tiền là {self.total_amount:,.0f} VNĐ.\nBạn có chắc chắn muốn thanh toán?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.cart_service.checkout(self.table_id):
                QMessageBox.information(self, "Thành công", f"Bàn {self.table_id} đã thanh toán xong!")
                self.close() # Đóng cửa sổ sau khi xong
            else:
                QMessageBox.critical(self, "Lỗi", "Đã xảy ra lỗi khi thanh toán!")