from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QPolygon, QColor, QPen, QFontDatabase, QBrush
from PyQt5.QtCore import QPoint, QRect
import math
import random
import os

class QtAnimationWidget(QWidget):
    animation_info_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(900, 500)
        self.setStyleSheet("background-color: black;")

        self.white = QColor(255, 255, 255)
        self.blue = QColor(0, 0, 255)
        self.green = QColor(0, 255, 0)
        self.black = QColor(0, 0, 0)
        self.gray = QColor(128, 128, 128)
        self.yellow = QColor(255, 255, 0)
        self.road_gray = QColor(50, 50, 50)
        self.line_white = QColor(255, 255, 255)
        self.red = QColor(255, 0, 0)
        self.brown = QColor(139, 69, 19)
        self.light_brown = QColor(160, 82, 45)
        self.dark_blue = QColor(0, 0, 139)
        self.light_blue = QColor(173, 216, 230)
        self.silver = QColor(192, 192, 192)
        self.dark_gray = QColor(64, 64, 64)
        self.orange = QColor(255, 165, 0)
        self.purple = QColor(128, 0, 128)
        self.cyan = QColor(0, 255, 255)

        self.car_colors = [self.blue, self.red, self.green, self.orange, self.purple, self.cyan]
        self.plate_prefixes = ['京', '沪', '粤', '苏', '浙', '鲁', '川', '渝']

        self.car_x = -200
        self.car_y = 450
        self.barrier_raised = False
        self.barrier_anim = 0
        self.car_speed = 0
        self.car_moving = False
        self.auto_mode_triggered = False
        self.car_passed = False
        self.barrier_lowering = False

        self.car_color = self.blue
        self.current_plate = "京A12345"
        self.current_type = 'small_car'

        self.is_running = False
        self.auto_demo = False
        self.is_first_draw = True
        self.last_plate = None

        font_db = QFontDatabase()
        font_path = os.path.join(os.path.dirname(__file__), "SimHei.ttf")
        print(f"字体文件路径: {os.path.abspath(font_path)}")
        try:
            if os.path.exists(font_path):
                font_id = font_db.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = font_db.applicationFontFamilies(font_id)
                    if font_families:
                        simhei_font = font_families[0]
                        self.font_chinese = QFont(simhei_font, 16)
                        self.font_large = QFont(simhei_font, 16)
                    else:
                        raise Exception("SimHei 字体家族未找到")
                else:
                    raise Exception("加载 SimHei.ttf 失败")
            else:
                raise Exception("项目文件夹中未找到 SimHei.ttf")
        except Exception as e:
            print(f"字体加载错误: {e}")
            try:
                self.font_chinese = QFont("Microsoft YaHei", 16)
                self.font_large = QFont("Microsoft YaHei", 16)
            except:
                print("Microsoft YaHei 加载失败，回退到 Arial")
                self.font_chinese = QFont("Arial", 16)
                self.font_large = QFont("Arial", 16)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.setInterval(33)

    def generate_random_car(self):
        color = random.choice(self.car_colors)
        prefix = random.choice(self.plate_prefixes)
        numbers = ''.join(random.choices('0123456789', k=5))
        plate = f"{prefix}{numbers}"
        car_type = random.choice(['small_car', 'small_car', 'large_car'])
        return color, plate, car_type

    def update_vehicle_info(self, plate_info):
        plate_text = plate_info.get('plate', '京A12345')
        car_type = plate_info.get('type', 'small_car')
        color_map = {'small_car': self.blue, 'large_car': self.red}
        self.car_color = color_map.get(car_type, self.blue)
        self.current_plate = plate_text
        self.current_type = car_type
        print(f"动画系统收到车辆更新: {plate_text}, 车型: {car_type}")

    def start_animation(self):
        print("启动动画")
        self.is_running = True
        self.auto_demo = False
        if not self.anim_timer.isActive():
            self.anim_timer.start()
            print("动画定时器已启动")

    def stop_animation(self):
        print("停止动画")
        self.is_running = False
        self.auto_demo = False
        if self.anim_timer.isActive():
            self.anim_timer.stop()
            print("动画定时器已停止")

    def start_auto_demo(self):
        print("启动自动演示")
        self.is_running = True
        self.auto_demo = True
        self.auto_mode_triggered = True
        self.car_moving = True
        self.car_speed = 3
        self.car_color, self.current_plate, self.current_type = self.generate_random_car()
        if not self.anim_timer.isActive():
            self.anim_timer.start()
            print("自动演示定时器已启动")

    def update_animation(self):
        try:
            if not self.is_running:
                print("动画未运行，状态：未启动")
                return
            dt = 1/60.0
            if self.auto_demo and self.auto_mode_triggered:
                if self.car_x > 350 and self.car_x < 450 and not self.barrier_raised and not self.barrier_lowering:
                    self.car_speed = 0
                    self.car_moving = False
                    self.barrier_raised = True
                    self.barrier_lowering = False
                    print("道闸抬起，车辆停止")
                if self.barrier_raised and self.barrier_anim > 0.95 and not self.car_moving:
                    self.car_moving = True
                    self.car_speed = 3
                    print("道闸完全抬起，车辆继续移动")
                if self.car_x > 650 and self.barrier_raised and not self.car_passed:
                    self.car_passed = True
                    self.barrier_raised = False
                    self.barrier_lowering = True
                    print("车辆通过，道闸开始放下")
                if self.barrier_lowering and self.barrier_anim < 0.05:
                    self.barrier_lowering = False
                    print("道闸完全放下")
                if self.car_x >= 900:
                    print(f"车辆超出范围，重置: {self.current_plate}")
                    self.car_color, self.current_plate, self.current_type = self.generate_random_car()
                    self.car_x = -200
                    self.car_y = 450
                    self.barrier_raised = False
                    self.barrier_anim = 0
                    self.car_speed = 3
                    self.car_moving = True
                    self.auto_mode_triggered = True
                    self.car_passed = False
                    self.barrier_lowering = False
                    self.is_first_draw = True
            if self.barrier_raised:
                self.barrier_anim = min(1.0, self.barrier_anim + dt * 1.5)
            elif self.barrier_lowering:
                self.barrier_anim = max(0.0, self.barrier_anim - dt * 1.5)
            if self.car_moving:
                self.car_x = int(self.car_x + self.car_speed * 60 * dt)
            if self.car_x > 900:
                print(f"车辆超出范围，重置: {self.current_plate}")
                self.car_color, self.current_plate, self.current_type = self.generate_random_car()
                self.car_x = -200
                self.car_y = 450
                self.barrier_raised = False
                self.barrier_anim = 0
                self.car_speed = 3
                self.car_moving = True
                self.auto_mode_triggered = True
                self.car_passed = False
                self.barrier_lowering = False
                self.is_first_draw = True
            self.animation_info_updated.emit({
                'car_position': self.car_x,
                'barrier_status': 'raised' if self.barrier_raised else 'lowered',
                'car_moving': self.car_moving,
                'current_plate': self.current_plate
            })
            self.update()
        except Exception as e:
            print(f"动画更新错误: {e}")
            self.stop_animation()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(0, 0, 900, 500, self.black)
            self.draw_road(painter)
            self.draw_booth(painter)
            self.draw_barrier(painter)
            self.draw_car(painter)
        except Exception as e:
            print(f"绘制错误: {e}")

    def draw_road(self, painter):
        if self.is_first_draw:
            print("绘制道路")
        painter.fillRect(0, 400, 900, 100, self.road_gray)
        pen = QPen(self.line_white, 4)
        painter.setPen(pen)
        for i in range(0, 900, 50):
            painter.drawLine(i, 450, i + 30, 450)

    def draw_booth(self, painter, x=350, y=250):
        try:
            painter.fillRect(x, y, 200, 200, self.brown)
            points = QPolygon([
                QPoint(x - 10, y),
                QPoint(x + 100, y - 80),
                QPoint(x + 210, y)
            ])
            painter.setBrush(QBrush(self.light_brown))
            painter.drawPolygon(points)
            painter.setBrush(Qt.NoBrush)
            pen = QPen(self.black, 3)
            painter.setPen(pen)
            painter.drawLine(x - 10, y, x + 210, y)
            painter.fillRect(x + 30, y + 40, 60, 50, self.light_blue)
            painter.drawRect(x + 30, y + 40, 60, 50)
            painter.drawLine(x + 60, y + 40, x + 60, y + 90)
            painter.fillRect(x + 110, y + 80, 60, 120, self.dark_blue)
            painter.drawRect(x + 110, y + 80, 60, 120)
            painter.fillRect(x + 140 - 6, y + 140 - 6, 12, 12, self.silver)
            painter.fillRect(x - 10, y + 200, 220, 20, self.dark_gray)
            painter.setFont(self.font_large)
            painter.setPen(self.white)
            painter.fillRect(x + 20, y - 80, 160, 40, self.black)
            painter.drawText(QRect(x + 20, y - 80, 160, 40), Qt.AlignCenter, "停车场岗亭")
        except Exception as e:
            print(f"绘制岗亭错误: {e}")

    def draw_barrier(self, painter, x=550, y=400):
        try:
            painter.fillRect(x - 30, y + 10, 60, 50, self.gray)
            painter.drawRect(x - 30, y + 10, 60, 50)
            painter.fillRect(x - 10, y - 100, 20, 110, self.silver)
            current_angle = 90 * self.barrier_anim if self.barrier_raised else 0
            end_x = int(x + 180 * math.cos(math.radians(current_angle)))
            end_y = int(y - 180 * math.sin(math.radians(current_angle)))
            pen = QPen(self.red, 20)
            painter.setPen(pen)
            painter.drawLine(x, y, end_x, end_y)
            for i in range(1, 5):
                stripe_pos = i / 5.0
                stripe_x = int(x + (end_x - x) * stripe_pos)
                stripe_y = int(y + (end_y - y) * stripe_pos)
                dx = int(6 * math.sin(math.radians(current_angle)))
                dy = int(6 * math.cos(math.radians(current_angle)))
                pen = QPen(self.white, 4)
                painter.setPen(pen)
                painter.drawLine(stripe_x - dx, stripe_y + dy, stripe_x + dx, stripe_y - dy)
            color = self.green if self.barrier_raised else self.red
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(end_x - 8), int(end_y - 8), 16, 16)
            painter.setBrush(QBrush(self.white))
            painter.drawEllipse(int(end_x - 4), int(end_y - 4), 8, 8)
            painter.setBrush(Qt.NoBrush)
        except Exception as e:
            print(f"绘制道闸错误: {e}")

    def draw_car(self, painter, angle=0):
        try:
            if self.is_first_draw or self.current_plate != self.last_plate:
                print(f"绘制车辆: 坐标=({self.car_x}, {self.car_y}), 类型={self.current_type}, 车牌={self.current_plate}")
                self.last_plate = self.current_plate
            if self.car_x < -300 or self.car_x > 900 or self.car_y < 0 or self.car_y > 500:
                print(f"车辆坐标超出范围: ({self.car_x}, {self.car_y})")
                return
            size = 160 if self.current_type == 'small_car' else 200
            width = 80 if self.current_type == 'small_car' else 100
            cos_a = math.cos(math.radians(angle))
            sin_a = math.sin(math.radians(angle))

            # 车身
            body_points = QPolygon([
                QPoint(
                    int(self.car_x - size / 2 * cos_a + width / 2 * sin_a),
                    int(self.car_y - size / 2 * sin_a - width / 2 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 2 * cos_a + width / 2 * sin_a),
                    int(self.car_y + size / 2 * sin_a - width / 2 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 2 * cos_a - width / 2 * sin_a),
                    int(self.car_y + size / 2 * sin_a + width / 2 * cos_a)
                ),
                QPoint(
                    int(self.car_x - size / 2 * cos_a - width / 2 * sin_a),
                    int(self.car_y - size / 2 * sin_a + width / 2 * cos_a)
                )
            ])
            painter.setBrush(QBrush(self.car_color))
            painter.drawPolygon(body_points)
            painter.setBrush(Qt.NoBrush)
            pen = QPen(self.black, 3)
            painter.setPen(pen)
            painter.drawPolygon(body_points)

            # 车头（前挡风玻璃）
            front_points = QPolygon([
                QPoint(
                    int(self.car_x + size / 2 * cos_a - width / 2 * sin_a),
                    int(self.car_y + size / 2 * sin_a + width / 2 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 2 * cos_a + width / 2 * sin_a),
                    int(self.car_y + size / 2 * sin_a - width / 2 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 2 * cos_a + width / 4 * sin_a),
                    int(self.car_y + size / 2 * sin_a - width / 4 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 2 * cos_a - width / 4 * sin_a),
                    int(self.car_y + size / 2 * sin_a + width / 4 * cos_a)
                )
            ])
            painter.setBrush(QBrush(self.dark_blue))
            painter.drawPolygon(front_points)
            painter.setPen(pen)
            painter.drawPolygon(front_points)

            # 车窗
            window_points = QPolygon([
                QPoint(
                    int(self.car_x - size / 4 * cos_a + width / 3 * sin_a),
                    int(self.car_y - size / 4 * sin_a - width / 3 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 4 * cos_a + width / 3 * sin_a),
                    int(self.car_y + size / 4 * sin_a - width / 3 * cos_a)
                ),
                QPoint(
                    int(self.car_x + size / 4 * cos_a - width / 3 * sin_a),
                    int(self.car_y + size / 4 * sin_a + width / 3 * cos_a)
                ),
                QPoint(
                    int(self.car_x - size / 4 * cos_a - width / 3 * sin_a),
                    int(self.car_y - size / 4 * sin_a + width / 3 * cos_a)
                )
            ])
            painter.setBrush(QBrush(self.light_blue))
            painter.drawPolygon(window_points)
            painter.setPen(pen)
            painter.drawPolygon(window_points)

            # 车轮
            wheel_size = 20
            wheel_positions = [
                (-size / 3, width / 3),
                (-size / 3, -width / 3),
                (size / 3, width / 3),
                (size / 3, -width / 3)
            ]
            painter.setBrush(QBrush(self.black))
            for dx, dy in wheel_positions:
                wheel_x = int(self.car_x + dx * cos_a + dy * sin_a)
                wheel_y = int(self.car_y + dx * sin_a - dy * cos_a)
                painter.drawEllipse(wheel_x - wheel_size // 2, wheel_y - wheel_size // 2, wheel_size, wheel_size)

            # 车牌（正上方）
            painter.setFont(self.font_chinese)
            painter.setPen(self.white)
            painter.fillRect(int(self.car_x - 60), int(self.car_y - width / 2 - 50), 120, 40, self.blue)
            painter.setPen(self.yellow)
            painter.drawText(QRect(int(self.car_x - 60), int(self.car_y - width / 2 - 50), 120, 40), Qt.AlignCenter, self.current_plate)

            self.is_first_draw = False
        except Exception as e:
            print(f"绘制车辆错误: {e}")