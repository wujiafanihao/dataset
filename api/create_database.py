import mysql.connector
from mysql.connector import Error
import json

def read_db_config():
    """
    读取数据库配置文件 'DBConfig.json' 并返回数据库配置信息。
    """
    with open('DBConfig.json', 'r') as config_file:
        config = json.load(config_file)
    return config['database']

def create_database_and_tables():
    """
    创建数据库和表。如果数据库或表已存在，则跳过创建步骤。
    """
    db_config = read_db_config()
    try:
        # 连接到MySQL服务器
        print("尝试连接到MySQL服务器...")
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )

        if connection.is_connected():
            print("成功连接到MySQL服务器")
            cursor = connection.cursor()

            # 创建数据库
            print(f"正在创建数据库 '{db_config['name']}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['name']}")
            print(f"数据库 '{db_config['name']}' 创建成功或已存在")

            # 使用数据库
            print(f"正在使用数据库 '{db_config['name']}'...")
            cursor.execute(f"USE {db_config['name']}")
            print(f"正在使用数据库 '{db_config['name']}' 成功")

            # 检查users表是否存在
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables 
                WHERE table_schema = %s
                AND table_name = 'users'
            """, (db_config['name'],))
            table_exists = cursor.fetchone()[0] == 1

            if not table_exists:
                # 创建 users 表
                print("正在创建表 'users'...")
                cursor.execute("""
                    CREATE TABLE users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        session_token VARCHAR(255),
                        last_login DATETIME
                    )
                """)
                print("表 'users' 创建成功")
            else:
                print("表 'users' 已存在")

            # 插入测试用户
            print("正在插入测试用户...")
            cursor.execute("""
                INSERT INTO users (username, password) 
                VALUES (%s, %s)
            """, ('root', '$2a$10$8qtmoS7k9yKm6JgA6M380.SzVRoEPYnzoXqt5YYmZn.qyADNuw0sO'))
            print("测试用户插入成功")

            # 提交事务
            connection.commit()
            print("事务已提交")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 连接已关闭")

if __name__ == "__main__":
    create_database_and_tables()