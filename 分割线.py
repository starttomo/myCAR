import sys
import cv2
import pytesseract
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox, QFrame,
                             QStackedWidget, QListWidget, QListWidgetItem, QGridLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSpinBox, QDoubleSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QTextCursor, QFont, QIcon

# Tesseract路径（Windows调整）- 请确保路径正确
pytesseract.pytesseract.tesseract_cmd = r'D:\tesseract\tesseract.exe'


class AnimationWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("动画演示")
        self.setGeometry(200, 200, 800, 600)

        # 初始化UI
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("动画演示窗口")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # 信息显示区域
        self.info_label = QLabel("等待接收车牌识别信息...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        layout.addWidget(self.info_label)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始动画")
        self.start_btn.clicked.connect(self.start_animation)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止动画")
        self.stop_btn.clicked.connect(self.stop_animation)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("状态: 未启动")
        layout.addWidget(self.status_label)

    def start_animation(self):
        self.status_label.setText("状态: 动画运行中")

    def stop_animation(self):
        self.status_label.setText("状态: 已停止")

    def update_plate_info(self, plate_info):
        """更新车牌信息（从主窗口接收）"""
        info_text = f"最新识别车牌: {plate_info.get('plate', '未知')}\n"
        info_text += f"车型: {plate_info.get('type', '未知')}\n"
        info_text += f"位置: {plate_info.get('bbox', '未知')}"
        self.info_label.setText(info_text)


class BillingRulesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("计费规则设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # 计费规则表格
        self.setup_billing_table(layout)

        # 添加规则按钮
        add_rule_btn = QPushButton("添加计费规则")
        add_rule_btn.clicked.connect(self.add_billing_rule)
        layout.addWidget(add_rule_btn)

        # 说明文本
        info_label = QLabel("说明: 系统将按照规则顺序进行匹配，第一个匹配的规则将被应用")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

    def setup_billing_table(self, layout):
        self.billing_table = QTableWidget()
        self.billing_table.setColumnCount(5)
        self.billing_table.setHorizontalHeaderLabels(["车型", "时间段", "首小时(元)", "后续每小时(元)", "操作"])

        # 设置表格属性
        self.billing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.billing_table.setSelectionBehavior(QTableWidget.SelectRows)

        # 添加示例数据
        self.add_sample_data()

        layout.addWidget(self.billing_table)

    def add_sample_data(self):
        # 清空表格
        self.billing_table.setRowCount(0)

        # 示例数据
        sample_rules = [
            {"type": "小型车", "time_range": "00:00-24:00", "first_hour": 5.0, "additional_hour": 2.0},
            {"type": "大型车", "time_range": "00:00-24:00", "first_hour": 10.0, "additional_hour": 5.0},
            {"type": "小型车", "time_range": "08:00-20:00", "first_hour": 8.0, "additional_hour": 3.0},
        ]

        for i, rule in enumerate(sample_rules):
            self.billing_table.insertRow(i)
            self.billing_table.setItem(i, 0, QTableWidgetItem(rule["type"]))
            self.billing_table.setItem(i, 1, QTableWidgetItem(rule["time_range"]))
            self.billing_table.setItem(i, 2, QTableWidgetItem(str(rule["first_hour"])))
            self.billing_table.setItem(i, 3, QTableWidgetItem(str(rule["additional_hour"])))

            # 操作按钮
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_rule(row))
            self.billing_table.setCellWidget(i, 4, delete_btn)

    def add_billing_rule(self):
        # 创建添加规则的对话框
        dialog = QWidget()
        dialog.setWindowTitle("添加计费规则")
        dialog.setFixedSize(300, 250)

        layout = QFormLayout(dialog)

        # 车型选择
        car_type_combo = QListWidget()
        car_type_combo.addItems(["小型车", "大型车", "摩托车", "其他"])
        car_type_combo.setFixedHeight(80)
        layout.addRow("车型:", car_type_combo)

        # 时间段
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

        # 费用设置
        first_hour_spin = QDoubleSpinBox()
        first_hour_spin.setRange(0, 1000)
        first_hour_spin.setValue(5.0)
        layout.addRow("首小时费用(元):", first_hour_spin)

        additional_hour_spin = QDoubleSpinBox()
        additional_hour_spin.setRange(0, 1000)
        additional_hour_spin.setValue(2.0)
        layout.addRow("后续每小时(元):", additional_hour_spin)

        # 按钮
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

                # 添加到表格
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


class VideoProcessor(QThread):
    frame_processed = pyqtSignal(np.ndarray, list)
    finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.is_running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error_occurred.emit(f"无法打开视频: {self.video_path}")
                return

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps / 10))  # 每秒处理10帧

            frame_count = 0
            all_results = []

            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    # 检测车牌
                    results = self.detect_plate_from_frame(frame.copy())

                    # 绘制检测框
                    processed_frame = self.draw_boxes_on_frame(frame.copy(), results)

                    # 更新结果
                    for result in results:
                        if result['plate'] not in [r['plate'] for r in all_results]:
                            all_results.append(result)

                    # 发送处理后的帧和结果
                    self.frame_processed.emit(processed_frame, results)

                frame_count += 1
                if not self.is_running:
                    break

            cap.release()
            self.finished.emit(all_results)

        except Exception as e:
            self.error_occurred.emit(f"视频处理错误: {str(e)}")

    def stop(self):
        self.is_running = False

    def detect_plate_from_frame(self, frame):
        """从视频帧检测车牌"""
        if frame is None:
            return []

        # 调整图像大小以提高处理速度
        height, width = frame.shape[:2]
        if width > 1000:
            scale = 1000 / width
            frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        edges = cv2.Canny(thresh, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        plates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            if 2 < aspect_ratio < 5 and w > 100 and h > 20:
                plate_img = gray[y:y + h, x:x + w]
                plate_img = cv2.convertScaleAbs(plate_img, alpha=1.5, beta=0)

                plate_text = pytesseract.image_to_string(
                    plate_img,
                    config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                ).strip()

                if len(plate_text) > 5 and any(c.isalpha() for c in plate_text) and any(
                        c.isdigit() for c in plate_text):
                    car_type = 'small_car' if w < 400 else 'large_car'
                    plates.append({
                        'plate': plate_text,
                        'type': car_type,
                        'bbox': (x, y, w, h)
                    })

        return plates

    def draw_boxes_on_frame(self, frame, results):
        """在帧上绘制检测框"""
        for result in results:
            x, y, w, h = result['bbox']
            # 绘制矩形框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 绘制车牌文本
            cv2.putText(frame, result['plate'], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame


class LicensePlateRecognizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能停车场管理系统")
        self.setGeometry(100, 100, 1400, 800)

        # 初始化变量
        self.image_path = None
        self.video_path = None
        self.video_processor = None
        self.current_pixmap = None
        self.animation_window = None

        self.init_ui()

    def init_ui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧侧边栏 (1/6)
        self.setup_sidebar(main_layout)

        # 右侧主内容区域 (5/6)
        self.setup_main_content(main_layout)

    def setup_sidebar(self, main_layout):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(200)
        sidebar_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(5, 20, 5, 20)

        # 标题
        title_label = QLabel("停车场管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        sidebar_layout.addWidget(title_label)

        sidebar_layout.addSpacing(20)

        # 功能按钮
        self.plate_recognition_btn = QPushButton("车牌识别")
        self.plate_recognition_btn.setMinimumHeight(40)
        self.plate_recognition_btn.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.plate_recognition_btn)

        self.animation_btn = QPushButton("动画演示")
        self.animation_btn.setMinimumHeight(40)
        self.animation_btn.clicked.connect(self.show_animation_window)
        sidebar_layout.addWidget(self.animation_btn)

        self.billing_rules_btn = QPushButton("计费规则")
        self.billing_rules_btn.setMinimumHeight(40)
        self.billing_rules_btn.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.billing_rules_btn)

        sidebar_layout.addStretch()

        # 退出按钮
        exit_btn = QPushButton("退出系统")
        exit_btn.setMinimumHeight(40)
        exit_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        exit_btn.clicked.connect(self.close_application)
        sidebar_layout.addWidget(exit_btn)

        main_layout.addWidget(sidebar_frame)

    def setup_main_content(self, main_layout):
        # 右侧内容区域
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # 页面1: 车牌识别
        self.plate_recognition_page = self.create_plate_recognition_page()
        self.stacked_widget.addWidget(self.plate_recognition_page)

        # 页面2: 计费规则
        self.billing_rules_page = BillingRulesPage()
        self.stacked_widget.addWidget(self.billing_rules_page)

        main_layout.addWidget(content_frame, 5)  # 右侧占5份

    def create_plate_recognition_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        # 左侧媒体显示区域 (3/4)
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Box)
        left_frame.setLineWidth(1)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.media_label = QLabel("请上传图片或视频")
        self.media_label.setAlignment(Qt.AlignCenter)
        self.media_label.setMinimumSize(800, 500)
        self.media_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        left_layout.addWidget(self.media_label)

        # 右侧控制区域 (1/4)
        right_frame = QFrame()
        right_frame.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(10)

        # 结果显示区域
        result_label = QLabel("识别结果:")
        result_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(300)
        self.result_text.setStyleSheet("border: 1px solid gray;")
        right_layout.addWidget(self.result_text)

        # 按钮区域
        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)

        self.upload_image_btn = QPushButton("上传图片")
        self.upload_image_btn.clicked.connect(self.upload_image)
        self.upload_image_btn.setMinimumHeight(40)
        button_layout.addWidget(self.upload_image_btn)

        self.upload_video_btn = QPushButton("上传视频")
        self.upload_video_btn.clicked.connect(self.upload_video)
        self.upload_video_btn.setMinimumHeight(40)
        button_layout.addWidget(self.upload_video_btn)

        self.recognize_btn = QPushButton("开始识别")
        self.recognize_btn.clicked.connect(self.start_recognition)
        self.recognize_btn.setMinimumHeight(40)
        self.recognize_btn.setStyleSheet("background-color: lightblue; font-weight: bold;")
        button_layout.addWidget(self.recognize_btn)

        self.stop_btn = QPushButton("停止识别")
        self.stop_btn.clicked.connect(self.stop_recognition)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setStyleSheet("background-color: lightcoral;")
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        right_layout.addWidget(button_frame)
        right_layout.addStretch()

        # 添加到主布局
        layout.addWidget(left_frame, 3)  # 左侧占3份
        layout.addWidget(right_frame, 1)  # 右侧占1份

        return page

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def show_animation_window(self):
        if self.animation_window is None:
            self.animation_window = AnimationWindow(self)
        self.animation_window.show()
        self.animation_window.raise_()  # 确保窗口在最前面

    def close_application(self):
        self.stop_recognition()
        QApplication.quit()

    def upload_image(self):
        self.stop_recognition()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if file_path:
            self.image_path = file_path
            self.video_path = None

            # 显示图片
            pixmap = QPixmap(file_path)
            self.display_media(pixmap)

            self.result_text.clear()
            self.result_text.append(f"已加载图片: {os.path.basename(file_path)}")

    def upload_video(self):
        self.stop_recognition()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv)"
        )
        if file_path:
            self.video_path = file_path
            self.image_path = None

            # 显示视频第一帧作为预览
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.display_media(pixmap)

            cap.release()

            self.result_text.clear()
            self.result_text.append(f"已加载视频: {os.path.basename(file_path)}")
            self.result_text.append("点击'开始识别'进行实时识别")

    def display_media(self, pixmap):
        """显示媒体内容"""
        if not pixmap.isNull():
            # 缩放以适应标签大小
            scaled_pixmap = pixmap.scaled(
                self.media_label.width() - 10,
                self.media_label.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.media_label.setPixmap(scaled_pixmap)
            self.current_pixmap = pixmap

    def resizeEvent(self, event):
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)
        if self.current_pixmap and not self.current_pixmap.isNull():
            self.display_media(self.current_pixmap)

    def start_recognition(self):
        if not self.image_path and not self.video_path:
            QMessageBox.warning(self, "警告", "请先上传图片或视频!")
            return

        self.recognize_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.result_text.clear()
        self.result_text.append("正在识别，请稍候...")

        if self.image_path:
            self.process_image()
        elif self.video_path:
            self.process_video()

    def stop_recognition(self):
        if self.video_processor:
            self.video_processor.stop()
            self.video_processor.wait()
            self.video_processor = None

        self.recognize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def process_image(self):
        try:
            results = self.detect_plate(self.image_path)
            self.display_results(results, "图片")

            # 发送到动画窗口
            if results and self.animation_window:
                self.animation_window.update_plate_info(results[0])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"识别过程中发生错误: {str(e)}")
        finally:
            self.stop_recognition()

    def process_video(self):
        if not self.video_path:
            return

        self.video_processor = VideoProcessor(self.video_path)
        self.video_processor.frame_processed.connect(self.update_video_frame)
        self.video_processor.finished.connect(self.on_video_finished)
        self.video_processor.error_occurred.connect(self.on_video_error)
        self.video_processor.start()

    def update_video_frame(self, frame, results):
        """更新视频帧显示"""
        # 转换OpenCV帧为QImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 显示帧
        pixmap = QPixmap.fromImage(q_img)
        self.display_media(pixmap)

        # 更新结果
        for result in results:
            self.add_result(result)

            # 发送到动画窗口
            if self.animation_window:
                self.animation_window.update_plate_info(result)

    def add_result(self, result):
        """添加单个识别结果"""
        current_text = self.result_text.toPlainText()
        if result['plate'] not in current_text:
            self.result_text.append(f"检测到车牌: {result['plate']}")
            self.result_text.append(f"车型: {result['type']}")
            self.result_text.append(f"位置: {result['bbox']}")
            self.result_text.append("-" * 30)

            # 自动滚动到底部
            cursor = self.result_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.result_text.setTextCursor(cursor)

    def on_video_finished(self, all_results):
        """视频处理完成"""
        self.result_text.append("\n" + "=" * 50)
        self.result_text.append(f"视频识别完成！共检测到 {len(all_results)} 个不同车牌:\n")

        for i, result in enumerate(all_results, 1):
            self.result_text.append(f"{i}. {result['plate']} ({result['type']})")

        self.stop_recognition()

    def on_video_error(self, error_msg):
        """视频处理错误"""
        QMessageBox.critical(self, "错误", error_msg)
        self.stop_recognition()

    def display_results(self, results, source_type):
        """显示识别结果"""
        if results:
            self.result_text.append(f"从{source_type}中识别到 {len(results)} 个车牌:\n")
            for i, result in enumerate(results, 1):
                self.result_text.append(f"{i}. 车牌号: {result['plate']}")
                self.result_text.append(f"   车型: {result['type']}")
                self.result_text.append(f"   位置: {result['bbox']}\n")
        else:
            self.result_text.append(f"未从{source_type}中识别到车牌")

    def detect_plate(self, image_path):
        """检测图片中的车牌"""
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"无法读取图像: {image_path}")

        # 调整图像大小以提高处理速度
        height, width = img.shape[:2]
        if width > 1000:
            scale = 1000 / width
            img = cv2.resize(img, (int(width * scale), int(height * scale)))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        edges = cv2.Canny(thresh, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        plates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            if 2 < aspect_ratio < 5 and w > 100 and h > 20:
                plate_img = gray[y:y + h, x:x + w]
                plate_img = cv2.convertScaleAbs(plate_img, alpha=1.5, beta=0)

                plate_text = pytesseract.image_to_string(
                    plate_img,
                    config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                ).strip()

                if len(plate_text) > 5 and any(c.isalpha() for c in plate_text) and any(
                        c.isdigit() for c in plate_text):
                    car_type = 'small_car' if w < 400 else 'large_car'
                    plates.append({
                        'plate': plate_text,
                        'type': car_type,
                        'bbox': (x, y, w, h)
                    })

                    # 在图像上绘制边界框
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img, plate_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 显示处理后的图像
        if plates:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channel = img_rgb.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.display_media(pixmap)

        return plates

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_recognition()
        if self.animation_window:
            self.animation_window.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicensePlateRecognizer()
    window.show()
    sys.exit(app.exec_())