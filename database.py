"""
数据库配置和连接管理
"""
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# 数据库文件路径
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "loler.db"

# 创建数据库引擎
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "check_same_thread": False,
        "isolation_level": None  # 使用autocommit模式，避免事务隔离问题
    }
)


def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session

