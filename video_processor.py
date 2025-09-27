# 视频处理模块
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


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
                    results = self.detect_plate_from_frame(frame.copy())
                    processed_frame = self.draw_boxes_on_frame(frame.copy(), results)

                    for result in results:
                        if result['plate'] not in [r['plate'] for r in all_results]:
                            all_results.append(result)

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
        """从视频帧检测车牌 - 可替换为YOLO实现"""
        if frame is None:
            return []

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

                plate_text = self.recognize_plate_text(plate_img)

                if len(plate_text) > 5 and any(c.isalpha() for c in plate_text) and any(
                        c.isdigit() for c in plate_text):
                    car_type = 'small_car' if w < 400 else 'large_car'
                    plates.append({
                        'plate': plate_text,
                        'type': car_type,
                        'bbox': (x, y, w, h)
                    })

        return plates

    def recognize_plate_text(self, plate_img):
        """车牌文字识别接口"""
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

    def draw_boxes_on_frame(self, frame, results):
        """在帧上绘制检测框"""
        for result in results:
            x, y, w, h = result['bbox']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, result['plate'], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame