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

def create_connection():
    """
    创建数据库连接。
    """
    db_config = read_db_config()
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['name']
        )
        if connection.is_connected():
            print("成功连接到MySQL服务器")
            return connection
    except Error as e:
        print(f"连接数据库时发生错误: {e}")
        return None

def close_connection(connection):
    """
    关闭数据库连接。
    """
    if connection.is_connected():
        connection.close()
        print("MySQL 连接已关闭")

def create_database_and_tables():
    """
    创建数据库和表。如果数据库或表已存在，则跳过创建步骤。
    """
    db_config = read_db_config()
    connection = None
    cursor = None
    try:
        # 连接到MySQL服务器
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = connection.cursor()

        # 创建数据库
        print(f"正在创建数据库 '{db_config['name']}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['name']}")
        print(f"数据库 '{db_config['name']}' 创建成功或已存在")

        # 使用数据库
        print(f"正在使用数据库 '{db_config['name']}'...")
        cursor.execute(f"USE {db_config['name']}")
        print(f"正在使用数据库 '{db_config['name']}' 成功")

        # 创建 users 表
        print("正在创建表 'users'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                session_token VARCHAR(255),
                last_login DATETIME
            )
        """)
        print("表 'users' 创建成功或已存在")

        # 插入测试用户
        print("正在插入测试用户...")
        cursor.execute("""
            INSERT IGNORE INTO users (username, password) 
            VALUES (%s, %s)
        """, ('root', '$2a$10$Gk8Y15QeXFna11e31qYKteBPHH9ClVIPakq1aYG56Lv3Z78T2AGSe'))  # 密码为 '251605'
        print("测试用户插入成功或已存在")

        # 创建 task 表
        print("正在创建表 'task'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                target INT NOT NULL COMMENT '今日未标注数量',
                completed INT NOT NULL COMMENT '已标注数量',
                status ENUM('未完成', '完成') NOT NULL DEFAULT '未完成',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("表 'task' 创建成功或已存在")

        # 创建 annotations 表
        print("正在创建表 'annotations'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                image_name VARCHAR(255) NOT NULL COMMENT '图片名称',
                annotation TEXT NOT NULL COMMENT '标注数据',
                status ENUM('未标注', '已标注') NOT NULL DEFAULT '未标注',
                FOREIGN KEY (task_id) REFERENCES task(id)
            )
        """)
        print("表 'annotations' 创建成功或已存在")

        # 提交事务
        connection.commit()
        print("事务已提交")

    except Error as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
            print("事务已回滚")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            close_connection(connection)

if __name__ == "__main__":
    create_database_and_tables()
