import uuid
from datetime import datetime
import bcrypt

class User:
    def __init__(self, db_helper):
        """
        初始化 User 类。
        :param db_helper: DBHelper 实例，用于数据库操作
        """
        self.db = db_helper

    def _hash_password(self, password):
        """
        使用 bcrypt 加密密码。
        :param password: 明文密码
        :return: 加密后的密码（字节串）
        """
        # 生成 salt 并哈希密码
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def _check_password(self, input_password, hashed_password):
        """
        验证输入的密码是否与加密后的密码匹配。
        :param input_password: 用户输入的密码
        :param hashed_password: 数据库中存储的加密密码
        :return: 如果匹配返回 True，否则返回 False
        """
        # 检查密码是否匹配
        return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register(self, username, password):
        """
        注册新用户。
        :param username: 用户名
        :param password: 明文密码
        :return: 注册成功返回 True，否则返回 False
        """
        # 检查用户名是否已存在
        existing_user = self.db.get_records('users', {'username': username})
        if existing_user:
            print("用户名已存在")
            return False

        # 加密密码
        hashed_password = self._hash_password(password)

        # 插入新用户
        user_data = {
            'username': username,
            'password': hashed_password.decode('utf-8'),  # 将字节串转换为字符串存储
            'session_token': None,
            'last_login': None
        }
        self.db.insert_record('users', user_data)
        print("用户注册成功")
        return True

    def login(self, username, password):
        """
        用户登录。
        :param username: 用户名
        :param password: 明文密码
        :return: 登录成功返回 session_token，否则返回 None
        """
        # 查询用户
        user = self.db.get_records('users', {'username': username})
        if not user:
            print("用户名或密码错误")
            return None

        user = user[0]

        # 验证密码
        if not self._check_password(password, user['password']):
            print("用户名或密码错误")
            return None

        # 检查用户是否已经在其他设备登录
        if user['session_token']:
            print("该用户已在其他设备登录")
            return None

        # 生成新的 session_token
        session_token = str(uuid.uuid4())
        # 更新用户的 session_token 和 last_login
        self.db.update_record('users', {'session_token': session_token, 'last_login': datetime.now()}, 'id', user['id'])
        print("用户登录成功")
        return session_token

    def logout(self, session_token):
        """
        用户注销。
        :param session_token: 用户的 session_token
        :return: 注销成功返回 True，否则返回 False
        """
        # 查询用户
        user = self.db.get_records('users', {'session_token': session_token})
        if not user:
            print("无效的 session_token")
            return False

        user = user[0]

        # 清除 session_token
        self.db.update_record('users', {'session_token': None}, 'id', user['id'])
        print("用户注销成功")
        return True

    def is_logged_in(self, session_token):
        """
        检查用户是否已登录。
        :param session_token: 用户的 session_token
        :return: 如果用户已登录返回 True，否则返回 False
        """
        # 查询用户
        user = self.db.get_records('users', {'session_token': session_token})
        if user:
            return True
        return False

    def get_user_by_token(self, session_token):
        """
        根据 session_token 获取用户信息。
        :param session_token: 用户的 session_token
        :return: 用户信息（字典形式），如果未找到返回 None
        """
        # 查询用户
        user = self.db.get_records('users', {'session_token': session_token})
        if user:
            return user[0]
        return None