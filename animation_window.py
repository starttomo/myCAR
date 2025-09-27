import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from parking_animation import QtAnimationWidget

class AnimationWindow(QMainWindow):
    plate_info_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        print("初始化 AnimationWindow")
        self.setWindowTitle("停车场动画演示")
        self.setGeometry(200, 200, 1000, 700)

        self.animation_widget = None
        self.current_plate_info = {}
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("停车场动画演示系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # 动画显示区域
        self.animation_widget = QtAnimationWidget()
        layout.addWidget(self.animation_widget)
        print("动画 widget 已添加")

        # 连接动画状态信号
        self.animation_widget.animation_info_updated.connect(self.update_status)

        # 信息显示区域
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)

        self.info_label = QLabel("等待接收车牌识别信息...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("border: 1px solid gray; padding: 10px; background-color: white;")
        info_layout.addWidget(self.info_label)

        # 状态显示
        self.status_label = QLabel("状态: 未启动")
        info_layout.addWidget(self.status_label)

        layout.addWidget(info_frame)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始动画")
        self.start_btn.clicked.connect(self.start_animation)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止动画")
        self.stop_btn.clicked.connect(self.stop_animation)
        button_layout.addWidget(self.stop_btn)

        self.auto_btn = QPushButton("自动演示")
        self.auto_btn.clicked.connect(self.start_auto_demo)
        button_layout.addWidget(self.auto_btn)

        layout.addLayout(button_layout)

        # 自动启动动画
        self.start_auto_demo()

    def start_animation(self):
        """开始动画"""
        if self.animation_widget:
            print("触发开始动画")
            self.animation_widget.start_animation()
            self.status_label.setText("状态: 动画运行中")

    def stop_animation(self):
        """停止动画"""
        if self.animation_widget:
            print("触发停止动画")
            self.animation_widget.stop_animation()
            self.status_label.setText("状态: 已停止")

    def start_auto_demo(self):
        """开始自动演示"""
        if self.animation_widget:
            print("触发自动演示")
            self.animation_widget.start_auto_demo()
            self.status_label.setText("状态: 自动演示中")

    def update_status(self, info):
        """更新状态标签"""
        status = info.get('barrier_status', 'lowered')
        moving = info.get('car_moving', False)
        plate = info.get('current_plate', '未知')
        self.status_label.setText(f"状态: {'自动演示中' if self.animation_widget.auto_demo else '动画运行中'}, 道闸: {status}, 车辆移动: {moving}, 车牌: {plate}")

    def update_plate_info(self, plate_info):
        """更新车牌信息（从主窗口接收）"""
        self.current_plate_info = plate_info

        info_text = f"最新识别车牌: {plate_info.get('plate', '未知')}\n"
        info_text += f"车型: {plate_info.get('type', '未知')}\n"
        info_text += f"位置: {plate_info.get('bbox', '未知')}"
        self.info_label.setText(info_text)

        # 将车牌信息传递给动画 widget
        if self.animation_widget:
            self.animation_widget.update_vehicle_info(plate_info)

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.animation_widget:
            self.animation_widget.stop_animation()
        event.accept()