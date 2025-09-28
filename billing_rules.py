# billing_rules.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDoubleSpinBox, QFormLayout,
                             QComboBox, QDateTimeEdit, QTextEdit, QMessageBox, QSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime
import mysql.connector
from datetime import datetime
import json
import math
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'zhang728',
    'database': 'parking'
}

class BillingRulesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        title_label = QLabel("计费规则与车辆信息管理")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title_label)
        rules_label = QLabel("计费规则设置")
        rules_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(rules_label)
        self.setup_billing_table(main_layout)
        rules_btn_layout = QHBoxLayout()
        add_rule_btn = QPushButton("添加计费规则")
        add_rule_btn.clicked.connect(self.add_billing_rule)
        save_rule_btn = QPushButton("保存计费规则")
        save_rule_btn.clicked.connect(self.save_rules_to_json)
        rules_btn_layout.addWidget(add_rule_btn)
        rules_btn_layout.addWidget(save_rule_btn)
        main_layout.addLayout(rules_btn_layout)
        info_label = QLabel("说明: 系统将按照规则顺序进行匹配，第一个匹配的规则将被应用")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)
        main_layout.addWidget(QLabel("<hr>"))
        vehicle_label = QLabel("车辆信息管理")
        vehicle_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(vehicle_label)
        self.setup_vehicle_management(main_layout)
        main_layout.addStretch()

    def setup_billing_table(self, layout):
        self.billing_table = QTableWidget()
        self.billing_table.setColumnCount(5)
        self.billing_table.setHorizontalHeaderLabels(["牌照颜色", "时间段", "首小时(元)", "后续每小时(元)", "折扣(%)"])
        self.billing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.billing_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.load_billing_rules()
        layout.addWidget(self.billing_table)

    def load_billing_rules(self):
        try:
            with open('billing_rules.json', 'r') as f:
                rules = json.load(f)
        except FileNotFoundError:
            rules = [
                {"plate_color": "blue", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0, "discount": 0.0},
                {"plate_color": "green", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0, "discount": 10.0}
            ]
        self.billing_table.setRowCount(0)
        for i, rule in enumerate(rules):
            self.billing_table.insertRow(i)
            self.billing_table.setItem(i, 0, QTableWidgetItem(rule["plate_color"]))
            self.billing_table.setItem(i, 1, QTableWidgetItem(rule["time_range"]))
            self.billing_table.setItem(i, 2, QTableWidgetItem(str(rule["first_hour"])))
            self.billing_table.setItem(i, 3, QTableWidgetItem(str(rule["additional_hour"])))
            self.billing_table.setItem(i, 4, QTableWidgetItem(str(rule["discount"])))
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_rule(row))
            self.billing_table.setCellWidget(i, 5, delete_btn)

    def save_rules_to_json(self):
        rules = []
        for row in range(self.billing_table.rowCount()):
            try:
                rules.append({
                    "plate_color": self.billing_table.item(row, 0).text(),
                    "time_range": self.billing_table.item(row, 1).text(),
                    "first_hour": float(self.billing_table.item(row, 2).text()),
                    "additional_hour": float(self.billing_table.item(row, 3).text()),
                    "discount": float(self.billing_table.item(row, 4).text())
                })
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存规则失败，第 {row + 1} 行数据无效: {e}")
                return
        try:
            with open('billing_rules.json', 'w') as f:
                json.dump(rules, f, indent=4)
            QMessageBox.information(self, "成功", "计费规则保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存规则到文件失败: {e}")
            logging.error(f"保存计费规则错误: {e}")

    def add_billing_rule(self):
        dialog = QWidget()
        dialog.setWindowTitle("添加计费规则")
        dialog.setFixedSize(300, 250)
        layout = QFormLayout(dialog)
        plate_color_combo = QComboBox()
        plate_color_combo.addItems(["blue", "green", "yellow"])
        layout.addRow("牌照颜色:", plate_color_combo)
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
        discount_spin = QDoubleSpinBox()
        discount_spin.setRange(0, 100)
        discount_spin.setValue(0.0)
        layout.addRow("折扣(%):", discount_spin)
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        def confirm_rule():
            time_range = f"{time_start.value():02d}:00-{time_end.value():02d}:00"
            if time_start.value() > time_end.value():
                QMessageBox.critical(dialog, "错误", "开始时间不能晚于结束时间")
                return
            row = self.billing_table.rowCount()
            self.billing_table.insertRow(row)
            self.billing_table.setItem(row, 0, QTableWidgetItem(plate_color_combo.currentText()))
            self.billing_table.setItem(row, 1, QTableWidgetItem(time_range))
            self.billing_table.setItem(row, 2, QTableWidgetItem(str(first_hour_spin.value())))
            self.billing_table.setItem(row, 3, QTableWidgetItem(str(additional_hour_spin.value())))
            self.billing_table.setItem(row, 4, QTableWidgetItem(str(discount_spin.value())))
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_rule(r))
            self.billing_table.setCellWidget(row, 5, delete_btn)
            dialog.close()

        confirm_btn.clicked.connect(confirm_rule)
        cancel_btn.clicked.connect(dialog.close)
        dialog.exec_()

    def delete_rule(self, row):
        self.billing_table.removeRow(row)
        self.save_rules_to_json()

    def setup_vehicle_management(self, layout):
        form_layout = QFormLayout()
        self.plate_combo = QComboBox()
        self.load_parking_plates()
        form_layout.addRow("车牌:", self.plate_combo)
        self.entry_time_edit = QDateTimeEdit()
        self.entry_time_edit.setCalendarPopup(True)
        self.entry_time_edit.setDateTime(QDateTime.currentDateTime())
        self.entry_time_edit.setReadOnly(True)  # 进入时间只读
        form_layout.addRow("进入时间:", self.entry_time_edit)
        self.exit_time_edit = QDateTimeEdit()
        self.exit_time_edit.setCalendarPopup(True)
        self.exit_time_edit.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("离开时间:", self.exit_time_edit)
        calc_btn = QPushButton("计算费用")
        calc_btn.clicked.connect(self.calculate_and_save_fee)
        form_layout.addRow(calc_btn)
        self.vehicle_info_text = QTextEdit()
        self.vehicle_info_text.setReadOnly(True)
        self.vehicle_info_text.setFixedHeight(100)
        form_layout.addRow("车辆信息:", self.vehicle_info_text)
        layout.addLayout(form_layout)

    def load_parking_plates(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT lp.plate_number, lp.plate_color, pr.entry_time
                FROM parking_records pr
                JOIN license_plates lp ON pr.plate_id = lp.plate_id
                WHERE pr.status = 'parking'
                """
            )
            plates = cursor.fetchall()
            cursor.close()
            conn.close()
            self.plate_combo.clear()
            if plates:
                for plate in plates:
                    self.plate_combo.addItem(
                        f"{plate['plate_number']} ({plate['plate_color']})",
                        {'plate_number': plate['plate_number'], 'plate_color': plate['plate_color'], 'entry_time': plate['entry_time']}
                    )
            else:
                self.plate_combo.addItem("无车辆", None)
            # 选择车牌时自动更新进入时间
            self.plate_combo.currentIndexChanged.connect(self.update_entry_time)
        except Exception as e:
            logging.error(f"加载停车车牌错误: {e}")
            QMessageBox.critical(self, "错误", f"加载停车车牌失败: {e}")

    def update_entry_time(self):
        """当选择车牌时，自动设置进入时间"""
        plate_data = self.plate_combo.currentData()
        if plate_data and 'entry_time' in plate_data:
            self.entry_time_edit.setDateTime(QDateTime(plate_data['entry_time']))
        else:
            self.entry_time_edit.setDateTime(QDateTime.currentDateTime())

    def calculate_and_save_fee(self):
        try:
            plate_data = self.plate_combo.currentData()
            if not plate_data:
                QMessageBox.critical(self, "错误", "未选择有效车牌")
                return
            plate_number = plate_data['plate_number']
            plate_color = plate_data['plate_color']
            entry_time = self.entry_time_edit.dateTime().toPyDateTime()
            exit_time = self.exit_time_edit.dateTime().toPyDateTime()
            if exit_time <= entry_time:
                QMessageBox.critical(self, "错误", "离开时间必须晚于进入时间")
                return
            total_amount = self.calculate_fee(entry_time, exit_time, plate_color)
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT record_id, space_id FROM parking_records
                WHERE plate_id = (SELECT plate_id FROM license_plates WHERE plate_number = %s)
                AND status = 'parking'
                """,
                (plate_number,)
            )
            record = cursor.fetchone()
            if record:
                cursor.execute(
                    "UPDATE parking_records SET exit_time = %s, status = 'completed' WHERE record_id = %s",
                    (exit_time, record['record_id'])
                )
                cursor.execute(
                    "UPDATE parking_spaces SET status = 'free' WHERE space_id = %s",
                    (record['space_id'],)
                )
                cursor.execute(
                    "INSERT INTO parking_fees (record_id, total_amount, payment_status) VALUES (%s, %s, %s)",
                    (record['record_id'], total_amount, 'unpaid')
                )
                conn.commit()
            cursor.close()
            conn.close()
            self.vehicle_info_text.setText(
                f"车牌: {plate_number} ({plate_color})\n"
                f"进入时间: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"离开时间: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"费用: {total_amount:.2f} 元"
            )
            self.load_parking_plates()
            QMessageBox.information(self, "成功", f"费用计算成功: {total_amount:.2f} 元")
        except Exception as e:
            logging.error(f"计算费用错误: {e}")
            QMessageBox.critical(self, "错误", f"计算费用失败: {e}")

    def calculate_fee(self, entry_time, exit_time, plate_color):
        duration_minutes = (exit_time - entry_time).total_seconds() / 60
        hours = max(1, math.ceil(duration_minutes / 60))
        try:
            with open('billing_rules.json', 'r') as f:
                rules = json.load(f)
        except FileNotFoundError:
            rules = [
                {"plate_color": "blue", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0, "discount": 0.0},
                {"plate_color": "green", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0, "discount": 10.0}
            ]
        current_hour = exit_time.hour
        for rule in rules:
            if rule['plate_color'] == plate_color:
                time_start, time_end = map(lambda x: int(x.split(':')[0]), rule['time_range'].split('-'))
                if time_start <= current_hour <= time_end or (time_end < time_start and (current_hour >= time_start or current_hour <= time_end)):
                    total = rule['first_hour'] + (hours - 1) * rule['additional_hour']
                    total *= (1 - rule['discount'] / 100)
                    return total
        return 0.0