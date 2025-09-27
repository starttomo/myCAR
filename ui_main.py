# 主界面UI
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox, QFrame,
                             QStackedWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QTextCursor, QFont

# 导入自定义模块
from video_processor import VideoProcessor
from animation_window import AnimationWindow
from billing_rules import BillingRulesPage


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

        main_layout.addWidget(content_frame, 5)

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
        layout.addWidget(left_frame, 3)
        layout.addWidget(right_frame, 1)

        return page

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def show_animation_window(self):
        print("尝试显示动画窗口")
        if self.animation_window is None:
            self.animation_window = AnimationWindow(self)
            print("动画窗口已创建")
        self.animation_window.show()
        self.animation_window.raise_()

    def close_application(self):
        self.stop_recognition()
        if self.animation_window:
            self.animation_window.close()
        QApplication.quit()

    def upload_image(self):
        self.stop_recognition()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if file_path:
            self.image_path = file_path
            self.video_path = None

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
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.media_label.width() - 10,
                self.media_label.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.media_label.setPixmap(scaled_pixmap)
            self.current_pixmap = pixmap

    def resizeEvent(self, event):
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
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        self.display_media(pixmap)

        for result in results:
            self.add_result(result)

            # 发送到动画窗口
            if self.animation_window:
                self.animation_window.update_plate_info(result)

    def add_result(self, result):
        current_text = self.result_text.toPlainText()
        if result['plate'] not in current_text:
            self.result_text.append(f"检测到车牌: {result['plate']}")
            self.result_text.append(f"车型: {result['type']}")
            self.result_text.append(f"位置: {result['bbox']}")
            self.result_text.append("-" * 30)

            cursor = self.result_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.result_text.setTextCursor(cursor)

    def on_video_finished(self, all_results):
        self.result_text.append("\n" + "=" * 50)
        self.result_text.append(f"视频识别完成！共检测到 {len(all_results)} 个不同车牌:\n")

        for i, result in enumerate(all_results, 1):
            self.result_text.append(f"{i}. {result['plate']} ({result['type']})")

        self.stop_recognition()

    def on_video_error(self, error_msg):
        QMessageBox.critical(self, "错误", error_msg)
        self.stop_recognition()

    def display_results(self, results, source_type):
        if results:
            self.result_text.append(f"从{source_type}中识别到 {len(results)} 个车牌:\n")
            for i, result in enumerate(results, 1):
                self.result_text.append(f"{i}. 车牌号: {result['plate']}")
                self.result_text.append(f"   车型: {result['type']}")
                self.result_text.append(f"   位置: {result['bbox']}\n")
        else:
            self.result_text.append(f"未从{source_type}中识别到车牌")

    def detect_plate(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"无法读取图像: {image_path}")

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

                plate_text = self.recognize_plate_text(plate_img)

                if len(plate_text) > 5 and any(c.isalpha() for c in plate_text) and any(
                        c.isdigit() for c in plate_text):
                    car_type = 'small_car' if w < 400 else 'large_car'
                    plates.append({
                        'plate': plate_text,
                        'type': car_type,
                        'bbox': (x, y, w, h)
                    })

                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img, plate_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if plates:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channel = img_rgb.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.display_media(pixmap)

        return plates

    def recognize_plate_text(self, plate_img):
        """车牌文字识别接口 - 便于后续替换为YOLO"""
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'D:\tesseract\tesseract.exe'

            plate_text = pytesseract.image_to_string(
                plate_img,
                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            ).strip()
            return plate_text
        except:
            return "OCR_ERROR"

    def closeEvent(self, event):
        self.stop_recognition()
        if self.animation_window:
            self.animation_window.close()
        event.accept()