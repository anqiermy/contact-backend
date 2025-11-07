import sqlite3
from sqlite3 import Connection
import os

# 数据库路径（项目根目录/data/contacts.db）
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'data',
    'contacts.db'
)


def get_db_connection() -> Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 支持按列名访问
    return conn


def init_db():
    """初始化数据库表结构（users、contacts、groups）"""
    # 创建data文件夹（如果不存在）
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db_connection()
    try:
        # 1. 用户表（存储注册信息）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 联系人表（关联用户）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                group_id INTEGER,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (phone, user_id)
            )
        ''')

        # 3. 分组表（关联用户）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (group_name, user_id)
            )
        ''')

        conn.commit()
        print("数据库表初始化成功：users、contacts、groups")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"初始化数据库失败：{str(e)}")
    finally:
        conn.close()


# 程序启动时自动初始化数据库
init_db()