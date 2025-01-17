import mysql.connector
from mysql.connector import Error
import json

class DBHelper:
    def __init__(self, config_file='DBConfig.json'):
        """
        初始化 DBHelper 类。
        :param config_file: 数据库配置文件的路径，默认为 'DBConfig.json'
        """
        # 读取数据库配置文件
        self.config = self.read_db_config(config_file)
        # 初始化数据库连接对象
        self.connection = None

    def read_db_config(self, config_file):
        """
        从 JSON 文件中读取数据库配置信息。
        :param config_file: 配置文件的路径
        :return: 数据库配置信息（字典形式）
        """
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config['database']

    def connect(self):
        """
        连接到 MySQL 数据库。
        如果连接成功，打印成功信息；否则捕获并打印错误信息。
        """
        try:
            print("尝试连接到MySQL服务器...")
            self.connection = mysql.connector.connect(
                host=self.config['host'],  # 数据库主机地址
                user=self.config['user'],  # 数据库用户名
                password=self.config['password'],  # 数据库密码
                database=self.config['name']  # 数据库名称
            )
            if self.connection.is_connected():
                print("成功连接到MySQL服务器")
        except Error as e:
            print(f"Error: {e}")

    def disconnect(self):
        """
        断开与 MySQL 数据库的连接。
        如果连接存在且已连接，则关闭连接并打印信息。
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL 连接已关闭")

    def execute_query(self, query, params=None):
        """
        执行 SQL 查询（用于插入、更新、删除等操作）。
        :param query: SQL 查询语句
        :param params: 查询参数（可选）
        """
        cursor = None
        try:
            # 如果未连接或连接已断开，则重新连接
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            # 执行 SQL 查询
            cursor.execute(query, params)
            # 提交事务
            self.connection.commit()
            print("查询执行成功")
        except Error as e:
            print(f"Error: {e}")
        finally:
            # 关闭游标
            if cursor:
                cursor.close()

    def fetch_all(self, query, params=None):
        """
        执行 SQL 查询并返回所有结果。
        :param query: SQL 查询语句
        :param params: 查询参数（可选）
        :return: 查询结果列表（字典形式）
        """
        cursor = None
        result = []
        try:
            # 如果未连接或连接已断开，则重新连接
            if not self.connection or not self.connection.is_connected():
                self.connect()

            # 使用字典游标，返回结果为字典形式
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            # 获取所有结果
            result = cursor.fetchall()
            print("数据获取成功")
        except Error as e:
            print(f"Error: {e}")
        finally:
            # 关闭游标
            if cursor:
                cursor.close()
        return result

    def fetch_one(self, query, params=None):
        """
        执行 SQL 查询并返回单条结果。
        :param query: SQL 查询语句
        :param params: 查询参数（可选）
        :return: 单条查询结果（字典形式）
        """
        cursor = None
        result = None
        try:
            # 如果未连接或连接已断开，则重新连接
            if not self.connection or not self.connection.is_connected():
                self.connect()

            # 使用字典游标，返回结果为字典形式
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            # 获取单条结果
            result = cursor.fetchone()
            print("单条数据获取成功")
        except Error as e:
            print(f"Error: {e}")
        finally:
            # 关闭游标
            if cursor:
                cursor.close()
        return result

    def insert_record(self, table_name, data):
        """
        插入记录到指定表。
        :param table_name: 表名
        :param data: 要插入的数据（字典形式，键为列名，值为数据）
        """
        # 构造列名和占位符
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        # 构造 SQL 插入语句
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        # 执行插入操作
        self.execute_query(query, tuple(data.values()))

    def update_record(self, table_name, data, condition_column, condition_value):
        """
        更新指定表中的记录。
        :param table_name: 表名
        :param data: 要更新的数据（字典形式，键为列名，值为数据）
        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        # 构造 SET 子句
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        # 构造 SQL 更新语句
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s"
        # 构造参数列表
        params = list(data.values()) + [condition_value]
        # 执行更新操作
        self.execute_query(query, tuple(params))

    def delete_record(self, table_name, condition_column, condition_value):
        """
        删除指定表中的记录。
        :param table_name: 表名
        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        # 构造 SQL 删除语句
        query = f"DELETE FROM {table_name} WHERE {condition_column} = %s"
        # 执行删除操作
        self.execute_query(query, (condition_value,))

    def get_records(self, table_name, conditions=None):
        """
        获取指定表中的记录。
        :param table_name: 表名
        :param conditions: 查询条件（字典形式，键为列名，值为条件值）
        :return: 查询结果列表（字典形式）
        """
        if conditions:
            # 构造 WHERE 子句
            where_clause = ' AND '.join([f"{key} = %s" for key in conditions.keys()])
            # 构造 SQL 查询语句
            query = f"SELECT * FROM {table_name} WHERE {where_clause}"
            # 执行查询并返回结果
            return self.fetch_all(query, tuple(conditions.values()))
        else:
            # 如果没有条件，查询所有记录
            query = f"SELECT * FROM {table_name}"
            return self.fetch_all(query)

    def get_record_by_id(self, table_name, record_id):
        """
        根据 ID 获取指定表中的单个记录。
        :param table_name: 表名
        :param record_id: 记录 ID
        :return: 单条查询结果（字典形式）
        """
        # 构造 SQL 查询语句
        query = f"SELECT * FROM {table_name} WHERE id = %s"
        # 执行查询并返回结果
        return self.fetch_one(query, (record_id,))