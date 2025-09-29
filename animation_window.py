from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from parking_animation import QtAnimationWidget
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnimationWindow(QMainWindow):
    plate_info_updated = pyqtSignal(dict)
    vehicle_action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("初始化 AnimationWindow")
        self.setWindowTitle("停车场动画演示")
        self.setGeometry(200, 200, 1000, 700)
        self.animation_widget = None
        self.current_plate_info = {}
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("停车场动画演示系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        self.animation_widget = QtAnimationWidget()
        self.animation_widget.setMinimumSize(900, 500)
        self.animation_widget.setStyleSheet("background-color: black; border: 1px solid white;")
        layout.addWidget(self.animation_widget)
        logging.info("动画 widget 已添加")

        self.animation_widget.animation_info_updated.connect(self.update_status)
        self.animation_widget.vehicle_action_requested.connect(self.handle_vehicle_action)

        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.info_label = QLabel("等待接收车牌识别信息...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("border: 1px solid gray; padding: 10px; background-color: white;")
        info_layout.addWidget(self.info_label)
        self.status_label = QLabel("状态: 未启动")
        info_layout.addWidget(self.status_label)
        layout.addWidget(info_frame)

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
        self.allow_entry_btn = QPushButton("允许进入")
        self.allow_entry_btn.clicked.connect(self.allow_entry)
        self.allow_entry_btn.setEnabled(False)
        button_layout.addWidget(self.allow_entry_btn)
        self.allow_exit_btn = QPushButton("允许离开")
        self.allow_exit_btn.clicked.connect(self.allow_exit)
        self.allow_exit_btn.setEnabled(False)
        button_layout.addWidget(self.allow_exit_btn)
        layout.addLayout(button_layout)

        self.show()
        self.raise_()
        self.activateWindow()
        self.start_auto_demo()

    def start_animation(self):
        if self.animation_widget and not self.animation_widget.is_running:
            logging.info("触发开始动画")
            self.animation_widget.start_animation()
            self.status_label.setText("状态: 动画运行中")

    def stop_animation(self):
        if self.animation_widget:
            logging.info("触发停止动画")
            self.animation_widget.stop_animation()
            self.status_label.setText("状态: 已停止")
            self.allow_entry_btn.setEnabled(False)
            self.allow_exit_btn.setEnabled(False)

    def start_auto_demo(self):
        if self.animation_widget and not self.animation_widget.is_running:
            logging.info("触发自动演示")
            self.animation_widget.start_auto_demo()
            self.status_label.setText("状态: 自动演示中")

    def allow_entry(self):
        if self.animation_widget:
            logging.info("触发允许进入")
            self.animation_widget.allow_entry()
            self.vehicle_action_triggered.emit("entry")
            self.allow_entry_btn.setEnabled(False)
            self.allow_exit_btn.setEnabled(False)

    def allow_exit(self):
        if self.animation_widget:
            logging.info("触发允许离开")
            self.animation_widget.allow_exit()
            self.vehicle_action_triggered.emit("exit")
            self.allow_entry_btn.setEnabled(False)
            self.allow_exit_btn.setEnabled(False)

    def handle_vehicle_action(self, action):
        if action.endswith("_waiting"):
            direction = action.split("_")[0]
            self.status_label.setText(f"状态: 车辆等待 {'进入' if direction == 'entry' else '离开'}，请管理员操作")
            self.allow_entry_btn.setEnabled(direction == 'entry')
            self.allow_exit_btn.setEnabled(direction == 'exit')
        elif action == "completed":
            self.status_label.setText("状态: 车辆已完成移动")
            self.allow_entry_btn.setEnabled(False)
            self.allow_exit_btn.setEnabled(False)

    def update_status(self, info):
        status = info.get('barrier_status', 'lowered')
        moving = info.get('car_moving', False)
        plate = info.get('current_plate', '未知')
        direction = info.get('direction', 'entry')
        self.status_label.setText(f"状态: {'自动演示中' if self.animation_widget.auto_demo else '动画运行中'}, 道闸: {'升起' if status == 'raised' else '下降'}, 车辆移动: {moving}, 车牌: {plate}, 方向: {'进入' if direction == 'entry' else '离开'}")

    def update_plate_info(self, plate_info):
        if self.animation_widget.is_running:
            logging.info(f"动画正在运行，忽略新车牌信息: {plate_info}")
            return
        self.current_plate_info = plate_info
        info_text = f"最新识别车牌: {plate_info.get('plate', '未知')}\n"
        info_text += f"车型: {plate_info.get('type', '未知')}\n"
        info_text += f"位置: {plate_info.get('bbox', '未知')}\n"
        info_text += f"车牌颜色: {plate_info.get('plate_color', '未知')}"
        self.info_label.setText(info_text)
        if self.animation_widget:
            self.animation_widget.update_vehicle_info(plate_info)

    def closeEvent(self, event):
        if self.animation_widget:
            self.animation_widget.stop_animation()
        event.accept()