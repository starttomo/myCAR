# 计费规则模块
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSpinBox, QDoubleSpinBox,
                             QFormLayout, QListWidget, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class BillingRulesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("计费规则设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        self.setup_billing_table(layout)

        add_rule_btn = QPushButton("添加计费规则")
        add_rule_btn.clicked.connect(self.add_billing_rule)
        layout.addWidget(add_rule_btn)

        info_label = QLabel("说明: 系统将按照规则顺序进行匹配，第一个匹配的规则将被应用")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

    def setup_billing_table(self, layout):
        self.billing_table = QTableWidget()
        self.billing_table.setColumnCount(5)
        self.billing_table.setHorizontalHeaderLabels(["车型", "时间段", "首小时(元)", "后续每小时(元)", "操作"])

        self.billing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.billing_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.add_sample_data()
        layout.addWidget(self.billing_table)

    def add_sample_data(self):
        self.billing_table.setRowCount(0)

        sample_rules = [
            {"type": "小型车", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0},
            {"type": "大型车", "time_range": "00:00-24:00", "first_hour": 10.0, "additional_hour": 5.0},
        ]

        for i, rule in enumerate(sample_rules):
            self.billing_table.insertRow(i)
            self.billing_table.setItem(i, 0, QTableWidgetItem(rule["type"]))
            self.billing_table.setItem(i, 1, QTableWidgetItem(rule["time_range"]))
            self.billing_table.setItem(i, 2, QTableWidgetItem(str(rule["first_hour"])))
            self.billing_table.setItem(i, 3, QTableWidgetItem(str(rule["additional_hour"])))

            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_rule(row))
            self.billing_table.setCellWidget(i, 4, delete_btn)

    def add_billing_rule(self):
        dialog = QWidget()
        dialog.setWindowTitle("添加计费规则")
        dialog.setFixedSize(300, 250)

        layout = QFormLayout(dialog)

        car_type_combo = QListWidget()
        car_type_combo.addItems(["小型车", "大型车", "摩托车", "其他"])
        car_type_combo.setFixedHeight(80)
        layout.addRow("车型:", car_type_combo)

        time_start = QSpinBox()
        time_start.setRange(0, 23)
        time_end = QSpinBox()
        time_end.setRange(0, 23)

        time_layout = QHBoxLayout()
        time_layout.addWidget(time_start)
        time_layout.addWidget(QLabel("时 -"))
        time_layout.addWidget(time_end)
        time_layout.addWidget(QLabel("时"))

        time_widget = QWidget()
        time_widget.setLayout(time_layout)
        layout.addRow("时间段:", time_widget)

        first_hour_spin = QDoubleSpinBox()
        first_hour_spin.setRange(0, 1000)
        first_hour_spin.setValue(5.0)
        layout.addRow("首小时费用(元):", first_hour_spin)

        additional_hour_spin = QDoubleSpinBox()
        additional_hour_spin.setRange(0, 1000)
        additional_hour_spin.setValue(2.0)
        layout.addRow("后续每小时(元):", additional_hour_spin)

        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认")
        cancel_btn = QPushButton("取消")

        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)

        def confirm_rule():
            selected_items = car_type_combo.selectedItems()
            if selected_items:
                car_type = selected_items[0].text()
                time_range = f"{time_start.value():02d}:00-{time_end.value():02d}:00"

                row = self.billing_table.rowCount()
                self.billing_table.insertRow(row)
                self.billing_table.setItem(row, 0, QTableWidgetItem(car_type))
                self.billing_table.setItem(row, 1, QTableWidgetItem(time_range))
                self.billing_table.setItem(row, 2, QTableWidgetItem(str(first_hour_spin.value())))
                self.billing_table.setItem(row, 3, QTableWidgetItem(str(additional_hour_spin.value())))

                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_rule(r))
                self.billing_table.setCellWidget(row, 4, delete_btn)

            dialog.close()

        def cancel_rule():
            dialog.close()

        confirm_btn.clicked.connect(confirm_rule)
        cancel_btn.clicked.connect(cancel_rule)

        dialog.exec_()

    def delete_rule(self, row):
        self.billing_table.removeRow(row)