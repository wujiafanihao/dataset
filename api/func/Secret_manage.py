import secrets
from datetime import datetime, timedelta
import threading

class SecretManager:
    def __init__(self):
        self.secret_key = self._generate_secret_key()  # 初始化 SECRET_KEY
        self._schedule_key_update()  # 启动定时任务，每 24 小时更新一次

    def _generate_secret_key(self):
        """
        生成一个 64 字节的安全随机字符串作为 SECRET_KEY。
        :return: 生成的 SECRET_KEY
        """
        return secrets.token_urlsafe(64)  # 生成 64 字节的 URL 安全字符串

    def _schedule_key_update(self):
        """
        每 24 小时更新一次 SECRET_KEY。
        """
        # 更新 SECRET_KEY
        self.secret_key = self._generate_secret_key()
        print(f"[{datetime.now()}] SECRET_KEY 已更新: {self.secret_key}")

        # 24 小时后再次调用自身
        threading.Timer(24 * 60 * 60, self._schedule_key_update).start()

    def get_secret_key(self):
        """
        获取当前的 SECRET_KEY。
        :return: 当前的 SECRET_KEY
        """
        return self.secret_key

# 初始化 SecretManager
secret_manager = SecretManager()