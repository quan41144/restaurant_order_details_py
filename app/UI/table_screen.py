import os
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QVBoxLayout, 
                             QLabel, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import TableService để lấy dữ liệu từ DB
from app.services.table_service import TableService

class TableScreen(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window # Lưu tham chiếu để gọi ngược lại MainWindow
        self.table_service = TableService(db)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sơ Đồ Bàn Nhà Hàng")
        self.setFixedSize(550, 450)
        
        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tiêu đề
        title = QLabel("CHỌN BÀN ĐANG PHỤC VỤ")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Chú thích màu sắc
        legend_layout = QGridLayout()
        lbl_empty = QLabel("🟢 Trống (Empty)")
        lbl_occupied = QLabel("🔴 Có khách (Occupied)")
        legend_layout.addWidget(lbl_empty, 0, 0)
        legend_layout.addWidget(lbl_occupied, 0, 1)
        layout.addLayout(legend_layout)

        # Grid chứa các bàn
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        
        # Lấy danh sách bàn từ Database
        tables = self.table_service.get_all_tables()

        for i, (t_id, t_name, t_status) in enumerate(tables):
            btn = QPushButton()
            # Hiển thị tên bàn và trạng thái
            btn.setText(f"{t_name}\n({t_status.upper()})")
            btn.setFixedSize(140, 100)
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            
            # --- THIẾT LẬP MÀU SẮC DỰA TRÊN TRẠNG THÁI ---
            if t_status == 'occupied':
                # Màu đỏ cho bàn có khách
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 12px;
                        border: 2px solid #c0392b;
                    }
                    QPushButton:hover {
                        background-color: #ff5e4d;
                    }
                """)
            else:
                # Màu xanh cho bàn trống
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 12px;
                        border: 2px solid #27ae60;
                    }
                    QPushButton:hover {
                        background-color: #34e07e;
                    }
                """)

            # Kết nối sự kiện click: Chọn bàn này
            btn.clicked.connect(lambda _, tid=t_id, tname=t_name: self.select_table(tid, tname))
            
            # Xếp bàn vào Grid (3 cột mỗi hàng)
            self.grid_layout.addWidget(btn, i // 3, i % 3)

        layout.addLayout(self.grid_layout)
        
        # Spacer đẩy các bàn lên trên
        layout.addStretch()

    def select_table(self, table_id, table_name):
        """Xử lý khi nhân viên bấm chọn một bàn"""
        try:
            # Gọi hàm cập nhật trên MainWindow
            if hasattr(self.main_window, 'update_selected_table'):
                self.main_window.update_selected_table(table_id, table_name)
                print(f"Đã chọn {table_name} (ID: {table_id})")
                self.close() # Đóng cửa sổ chọn bàn
            else:
                print("Lỗi: MainWindow không có hàm update_selected_table")
        except Exception as e:
            print(f"Lỗi khi chọn bàn: {e}")