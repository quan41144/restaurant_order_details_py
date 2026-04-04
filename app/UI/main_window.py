# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QLabel, QMessageBox, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import các màn hình chức năng
from app.UI.menu_screen import MenuScreen
from app.UI.checkout_screen import CheckoutScreen
from app.UI.table_screen import TableScreen

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        # Trạng thái bàn đang được chọn thao tác
        self.current_table_id = None
        self.current_table_name = "Chưa chọn bàn"

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Hệ Thống Quản Lý Nhà Hàng")
        self.setFixedSize(450, 650)
        
        # Widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # --- LOGO & TIÊU ĐỀ ---
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("RESTAURANT POS")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        
        subtitle = QLabel("Quản lý Đơn hàng & Thanh toán")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header_frame)

        # --- KHUNG HIỂN THỊ TRẠNG THÁI BÀN ---
        self.status_card = QFrame()
        self.status_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #ecf0f1;
                border-radius: 15px;
            }
        """)
        status_layout = QVBoxLayout(self.status_card)
        
        self.lbl_table_info = QLabel(f"📍 {self.current_table_name}")
        self.lbl_table_info.setFont(QFont("Segoe UI", 13, QFont.Medium))
        self.lbl_table_info.setAlignment(Qt.AlignCenter)
        self.lbl_table_info.setStyleSheet("color: #34495e; border: none;")
        
        status_layout.addWidget(self.lbl_table_info)
        main_layout.addWidget(self.status_card)

        # --- CÁC NÚT ĐIỀU HƯỚNG ---
        
        # 1. Nút Sơ đồ bàn (Màu Xám xanh)
        self.btn_tables = self.create_nav_button("🪑 CHỌN BÀN PHỤC VỤ", "#34495e")
        self.btn_tables.clicked.connect(self.open_table_selection)
        main_layout.addWidget(self.btn_tables)

        # 2. Nút Thực đơn (Màu Xanh lá)
        self.btn_menu = self.create_nav_button("📋 GỌI MÓN / MENU", "#27ae60")
        self.btn_menu.clicked.connect(self.open_menu)
        main_layout.addWidget(self.btn_menu)

        # 3. Nút Thanh toán (Màu Xanh dương)
        self.btn_checkout = self.create_nav_button("💰 THANH TOÁN", "#2980b9")
        self.btn_checkout.clicked.connect(self.open_checkout)
        main_layout.addWidget(self.btn_checkout)

        # Spacer đẩy nội dung lên trên
        main_layout.addStretch()

        # Footer
        footer = QLabel("© 2026 Restaurant Management System")
        footer.setFont(QFont("Arial", 8))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #bdc3c7;")
        main_layout.addWidget(footer)

    def create_nav_button(self, text, color):
        """Hàm tạo nút bấm với Style đồng nhất"""
        btn = QPushButton(text)
        btn.setFixedHeight(70)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color};
                margin-top: -2px;
                border-bottom: 4px solid rgba(0,0,0,0.2);
            }}
            QPushButton:pressed {{
                background-color: #2c3e50;
            }}
        """)
        return btn

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN ---

    def open_table_selection(self):
        """Mở sơ đồ bàn"""
        self.table_window = TableScreen(self.db, self)
        self.table_window.show()

    def update_selected_table(self, table_id, table_name):
        """Hàm được gọi từ TableScreen để cập nhật bàn đang chọn"""
        self.current_table_id = table_id
        self.current_table_name = table_name
        self.lbl_table_info.setText(f"📍 Đang phục vụ: {table_name}")
        self.lbl_table_info.setStyleSheet("color: #e67e22; font-weight: bold; border: none;")
        self.status_card.setStyleSheet("QFrame { background-color: #fff3e0; border: 2px solid #ffcc80; border-radius: 15px; }")

    def open_menu(self):
        """Mở menu gọi món (Yêu cầu chọn bàn trước)"""
        if self.current_table_id is None:
            # Sửa lại chuỗi tiếng Việt cho chuẩn
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn bàn trên sơ đồ trước khi gọi món!")
            return
        
        # Mở màn hình Menu
        self.menu_window = MenuScreen(self.db)
        # Gán ID bàn hiện tại sang MenuScreen để thực hiện lưu món
        self.menu_window.current_table_id = self.current_table_id
        self.menu_window.show()

    def open_checkout(self):
        """Mở màn hình thanh toán (Yêu cầu chọn bàn trước)"""
        if self.current_table_id is None:
            QMessageBox.warning(self, "Nhắc nhở", "Vui lòng chọn bàn cần thanh toán!")
            return
            
        self.checkout_window = CheckoutScreen(self.db, self.current_table_id)
        # Sau khi thanh toán xong, ta reset trạng thái trên MainWindow
        self.checkout_window.closeEvent = lambda event: self.reset_after_checkout()
        self.checkout_window.show()

    def reset_after_checkout(self):
        """Reset trạng thái MainWindow sau khi khách trả tiền và đi"""
        # Kiểm tra xem đơn hàng đã được xóa chưa (trạng thái bàn trong DB)
        # Nếu bàn đã trống thì reset giao diện
        self.current_table_id = None
        self.current_table_name = "Chưa chọn bàn"
        self.lbl_table_info.setText(f"📍 {self.current_table_name}")
        self.lbl_table_info.setStyleSheet("color: #34495e; border: none;")
        self.status_card.setStyleSheet("QFrame { background-color: #ffffff; border: 2px solid #ecf0f1; border-radius: 15px; }")