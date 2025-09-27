import mysql.connector
from datetime import datetime

# 数据库连接
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'zhang728',  # 你的密码
    'database': 'parking_db'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# 创建表（第一次运行）
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plate_number VARCHAR(20) NOT NULL,
            car_type VARCHAR(20) NOT NULL,
            entry_time DATETIME NOT NULL,
            exit_time DATETIME,
            fee DECIMAL(10,2) DEFAULT 0.00
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("数据库初始化完成！")

# 插入入场记录
def insert_entry(plate, car_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vehicles (plate_number, car_type, entry_time) VALUES (%s, %s, %s)",
                   (plate, car_type, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# 更新出场并计算费用
def update_exit(plate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET exit_time = %s WHERE plate_number = %s AND exit_time IS NULL",
                   (datetime.now(), plate))
    # 计算费用（假设查到记录）
    cursor.execute("SELECT car_type, entry_time FROM vehicles WHERE plate_number = %s AND exit_time IS NULL", (plate,))
    result = cursor.fetchone()
    if result:
        car_type, entry_time = result
        minutes = (datetime.now() - entry_time).total_seconds() / 60
        from config import calculate_fee
        fee = calculate_fee(car_type, minutes)
        cursor.execute("UPDATE vehicles SET fee = %s WHERE plate_number = %s AND exit_time IS NULL", (fee, plate))
        conn.commit()
    cursor.close()
    conn.close()
    return fee if result else 0

# 查询所有记录（供管理界面用）
def get_all_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY entry_time DESC")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records

# 测试
if __name__ == "__main__":
    init_db()  # 只跑一次
    insert_entry('京A12345', 'small_car')
    fee = update_exit('京A12345')
    print(f"费用: {fee}")
    print(get_all_records())