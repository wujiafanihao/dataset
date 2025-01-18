from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional

from db.DBHelper import DBHelper
from func.User import User

from func.Secret_manage import secret_manager

# 初始化 FastAPI 应用
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，或者指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# 初始化数据库和用户管理
db_helper = DBHelper()
user_manager = User(db_helper)

# JWT 配置
ALGORITHM = "HS256"  # JWT 签名算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token 过期时间（分钟）

# OAuth2 密码模式，用于验证 Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic 模型：定义登录请求的数据结构
class LoginRequest(BaseModel):
    username: str  # 用户名
    password: str  # 密码
    remember_me: bool = False  # 是否记住密码
    auto_login: bool = False  # 是否自动登录

# Pydantic 模型：定义 Token 返回的数据结构
class Token(BaseModel):
    access_token: str  # JWT Token
    token_type: str  # Token 类型（通常是 "bearer"）

# 登录接口
@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    用户登录接口。
    :param login_data: 包含用户名和密码的请求体
    :return: 返回 JWT Token
    """
    # 调用 User 类的登录方法
    session_token = user_manager.login(login_data.username, login_data.password)
    if not session_token:
        # 如果登录失败，返回 401 错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username, "session_token": session_token},  # 包含用户名和 session_token 的 payload
        expires_delta=access_token_expires,  # 设置 Token 过期时间
    )

    # 返回生成的 Token
    return {"access_token": access_token, "token_type": "bearer"}

# 创建 JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    生成 JWT Token。
    :param data: 包含用户信息的字典
    :param expires_delta: Token 过期时间
    :return: 生成的 JWT Token
    """
    to_encode = data.copy()  # 复制数据
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta  # 计算过期时间
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # 默认 15 分钟过期
    to_encode.update({"exp": expire})  # 添加过期时间到 payload
    encoded_jwt = jwt.encode(to_encode, secret_manager.get_secret_key(), algorithm=ALGORITHM)  # 使用 SecretManager 的 SECRET_KEY
    return encoded_jwt

# 验证 JWT Token
def verify_token(token: str = Depends(oauth2_scheme)):
    """
    验证 JWT Token 是否有效。
    :param token: 从请求头中提取的 Token
    :return: 如果 Token 有效，返回用户信息；否则抛出 401 错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的 Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 Token
        payload = jwt.decode(token, secret_manager.get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # 获取用户名
        session_token: str = payload.get("session_token")  # 获取 session_token
        if username is None or session_token is None:
            # 如果 Token 中缺少必要信息，抛出错误
            raise credentials_exception
    except jwt.PyJWTError:
        # 如果 Token 解码失败，抛出错误
        raise credentials_exception

    # 检查 session_token 是否有效
    user = user_manager.get_user_by_token(session_token)
    if not user:
        # 如果 session_token 无效，抛出错误
        raise credentials_exception

    # 返回用户信息
    return user

# 受保护的路由示例：仪表盘页面
@app.get("/dashboard")
async def dashboard(current_user: dict = Depends(verify_token)):
    """
    受保护的路由，只有登录用户才能访问。
    :param current_user: 通过 verify_token 验证的用户信息
    :return: 返回欢迎信息
    """
    return {"message": f"欢迎回来, {current_user['username']}!"}

# 启动 FastAPI 服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  