from app import init_db, DB_PATH
import os

# 确保运行时目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db()
print("✅ 数据库初始化完成")
