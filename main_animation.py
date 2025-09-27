import pygame
import sys
import time
import math
import random
import os
from PyQt5.QtCore import QPoint,QRect
from PyQt5.QtGui import  QPolygon, QColor, QPen,QBrush
from PyQt5 import Qt
# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Parking System Animation")
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (50, 50, 50)
LINE_WHITE = (255, 255, 255)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (160, 82, 45)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
SILVER = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# 车辆颜色列表
CAR_COLORS = [BLUE, RED, GREEN, ORANGE, PURPLE, CYAN]

# 车牌前缀列表
PLATE_PREFIXES = ['京', '沪', '粤', '苏', '浙', '鲁', '川', '渝']

# 加载中文字体
try:
    font_chinese = pygame.font.SysFont('SimHei', 24)
    font_large = pygame.font.SysFont('SimHei', 32)
except:
    font_chinese = pygame.font.Font(None, 24)
    font_large = pygame.font.Font(None, 32)


# 生成随机车辆
def generate_random_car():
    color = random.choice(CAR_COLORS)
    prefix = random.choice(PLATE_PREFIXES)
    numbers = ''.join(random.choices('0123456789', k=5))
    plate = f"{prefix}{numbers}"
    car_type = random.choice(['small_car', 'small_car', 'large_car'])  # 小车概率更高
    return color, plate, car_type


# 精细绘制函数
def draw_road(screen):
    """绘制道路"""
    pygame.draw.rect(screen, ROAD_GRAY, (0, 500, 1200, 300))
    for i in range(0, 1200, 50):
        pygame.draw.line(screen, LINE_WHITE, (i, 550), (i + 30, 550), 4)


def draw_booth(self, painter, x=500, y=350):
    painter.fillRect(x, y, 200, 200, self.brown)

    points = QPolygon([
        QPoint(x - 10, y),
        QPoint(x + 100, y - 80),
        QPoint(x + 210, y)
    ])
    # 替换 fillPolygon
    painter.setBrush(QBrush(self.light_brown))
    painter.drawPolygon(points)
    painter.setBrush(Qt.NoBrush)  # 清除画刷以免影响后续绘制
    pen = QPen(self.black, 3)
    painter.setPen(pen)
    painter.drawLine(x - 10, y, x + 210, y)

    # 窗户等细节（保持不变）
    painter.fillRect(x + 30, y + 40, 60, 50, self.light_blue)
    painter.drawRect(x + 30, y + 40, 60, 50)
    painter.drawLine(x + 60, y + 40, x + 60, y + 90)

    painter.fillRect(x + 110, y + 80, 60, 120, self.dark_blue)
    painter.drawRect(x + 110, y + 80, 60, 120)
    painter.fillRect(x + 140 - 6, y + 140 - 6, 12, 12, self.silver)

    painter.fillRect(x - 10, y + 200, 220, 20, self.dark_gray)

    painter.setFont(self.font_chinese)
    painter.setPen(self.white)
    painter.drawText(QRect(x + 100 - 50, y + 160 - 12, 100, 24), Qt.AlignCenter, "停车场岗亭")


def draw_barrier(self, painter, x=700, y=450):
    try:
        # 道闸底座
        painter.fillRect(x - 30, y + 10, 60, 50, self.gray)
        painter.drawRect(x - 30, y + 10, 60, 50)

        # 道闸立柱
        painter.fillRect(x - 10, y - 100, 20, 110, self.silver)

        # 道闸杆
        current_angle = 90 * self.barrier_anim if self.barrier_raised else 0
        end_x = x + 180 * math.cos(math.radians(current_angle))
        end_y = y - 180 * math.sin(math.radians(current_angle))

        pen = QPen(self.red, 20)
        painter.setPen(pen)
        painter.drawLine(x, y, end_x, end_y)

        # 条纹
        for i in range(1, 5):
            stripe_pos = i / 5.0
            stripe_x = x + (end_x - x) * stripe_pos
            stripe_y = y + (end_y - y) * stripe_pos
            dx = 6 * math.sin(math.radians(current_angle))
            dy = 6 * math.cos(math.radians(current_angle))
            pen = QPen(self.white, 4)
            painter.setPen(pen)
            painter.drawLine(stripe_x - dx, stripe_y + dy, stripe_x + dx, stripe_y - dy)

        # 道闸灯
        color = self.green if self.barrier_raised else self.red
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(end_x - 8), int(end_y - 8), 16, 16)  # 使用椭圆绘制灯
        painter.setBrush(QBrush(self.white))
        painter.drawEllipse(int(end_x - 4), int(end_y - 4), 8, 8)
        painter.setBrush(Qt.NoBrush)
    except Exception as e:
        print(f"绘制道闸错误: {e}")

def draw_car(self, painter, angle=0):
    try:
        if self.car_x < -300 or self.car_x > 1200 or self.car_y < 0 or self.car_y > 500:
            print(f"车辆坐标超出范围: ({self.car_x}, {self.car_y})")
            return
        size = 160 if self.current_type == 'small_car' else 200
        width = 80 if self.current_type == 'small_car' else 100

        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))

        points = QPolygon([
            QPoint(self.car_x - size / 2 * cos_a + width / 2 * sin_a, self.car_y - size / 2 * sin_a - width / 2 * cos_a),
            QPoint(self.car_x + size / 2 * cos_a + width / 2 * sin_a, self.car_y + size / 2 * sin_a - width / 2 * cos_a),
            QPoint(self.car_x + size / 2 * cos_a - width / 2 * sin_a, self.car_y + size / 2 * sin_a + width / 2 * cos_a),
            QPoint(self.car_x - size / 2 * cos_a - width / 2 * sin_a, self.car_y - size / 2 * sin_a + width / 2 * cos_a)
        ])
        # 替换 fillPolygon
        painter.setBrush(QBrush(self.car_color))
        painter.drawPolygon(points)
        painter.setBrush(Qt.NoBrush)  # 清除画刷
        pen = QPen(self.black, 3)
        painter.setPen(pen)
        painter.drawPolygon(points)

        # 车牌
        painter.setFont(self.font_chinese)
        painter.setPen(self.yellow)
        painter.fillRect(self.car_x - 40, self.car_y + 30, 80, 20, self.blue)
        painter.drawText(QRect(self.car_x - 40, self.car_y + 30, 80, 20), Qt.AlignCenter, self.current_plate)
    except Exception as e:
        print(f"绘制车辆错误: {e}")


# 主程序
def main():
    # 初始化状态
    car_x = -200
    car_y = 600
    barrier_raised = False
    barrier_anim = 0
    car_speed = 0
    car_moving = False
    auto_mode_triggered = False
    car_passed = False
    barrier_lowering = False

    # 生成第一辆随机车辆
    car_color, current_plate, current_type = generate_random_car()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                auto_mode_triggered = True
                car_moving = True
                car_speed = 3

        # 自动模式逻辑
        if auto_mode_triggered:
            # 车辆接近停车杆时停下
            if car_x > 550 and car_x < 650 and not barrier_raised and not barrier_lowering:
                car_speed = 0
                car_moving = False
                barrier_raised = True  # 自动抬起停车杆
                barrier_lowering = False

            # 停车杆完全抬起后车辆继续前进
            if barrier_raised and barrier_anim > 0.95 and not car_moving:
                car_moving = True
                car_speed = 3

            # 车辆完全通过后开始放下停车杆
            if car_x > 850 and barrier_raised and not car_passed:
                car_passed = True
                barrier_raised = False  # 开始下降
                barrier_lowering = True

            # 停车杆完全放下后重置状态
            if barrier_lowering and barrier_anim < 0.05:
                barrier_lowering = False

            # 车辆离开屏幕后重置
            if car_x >= 1200:
                # 生成新的随机车辆
                car_color, current_plate, current_type = generate_random_car()
                car_x = -200
                barrier_raised = False
                barrier_anim = 0
                car_speed = 0
                car_moving = False
                auto_mode_triggered = False
                car_passed = False
                barrier_lowering = False
                print("新一轮开始，生成新车辆")

        # 更新停车杆动画 - 上升和下降速度保持一致
        if barrier_raised:
            barrier_anim = min(1.0, barrier_anim + dt * 1.5)  # 稍微减慢速度
        elif barrier_lowering:
            barrier_anim = max(0.0, barrier_anim - dt * 1.5)  # 下降速度与上升一致

        # 车辆移动
        if car_moving:
            car_x += car_speed * 60 * dt

        # 绘制
        screen.fill(SKY_BLUE)  # 只保留天空背景
        draw_road(screen)
        draw_booth(screen, x=500, y=450)
        barrier_end_x = draw_barrier(screen, x=700, y=550, raised=barrier_raised, anim_progress=barrier_anim)

        if -200 < car_x < 1200:
            draw_car(screen, car_x, car_y, car_color, current_type, current_plate)

        # 显示信息
        mode_text = font_chinese.render("模式: 自动", True, BLACK)
        screen.blit(mode_text, (50, 50))

        status_text = font_chinese.render(
            f"车辆: {'移动中' if car_moving else '停止'} | 停车杆: {'抬起' if barrier_raised else '下降中' if barrier_lowering else '放下'}", True, BLACK)
        screen.blit(status_text, (50, 80))

        plate_text = font_chinese.render(f"车牌: {current_plate}", True, BLACK)
        screen.blit(plate_text, (50, 110))

        if not auto_mode_triggered:
            auto_text = font_chinese.render("按空格键开始自动演示", True, BLACK)
            screen.blit(auto_text, (50, 140))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()