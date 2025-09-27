# 收费标准配置（字典，便于修改）
PRICING = {
    'small_car': {'hourly_rate': 5, 'free_minutes': 60},  # 小型车：每小时5元，免费60分钟
    'large_car': {'hourly_rate': 10, 'free_minutes': 60}   # 大型车：每小时10元，免费60分钟
}

def calculate_fee(car_type, parking_minutes):
    """计算收费函数"""
    if parking_minutes <= PRICING[car_type]['free_minutes']:
        return 0
    else:
        hours = (parking_minutes - PRICING[car_type]['free_minutes']) / 60
        return round(hours * PRICING[car_type]['hourly_rate'], 2)

# 测试：运行python config.py
if __name__ == "__main__":
    print(calculate_fee('small_car', 120))  # 输出: 5.0