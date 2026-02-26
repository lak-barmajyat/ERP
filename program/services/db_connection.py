from functools import wraps
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    echo=False,            # True فقط أثناء التطوير/التشخيص
    future=True,           # API حديث
    pool_pre_ping=True,    # يتأكد أن الاتصال حي
    pool_size=10,          # اتصالات ثابتة في الـ pool
    max_overflow=20,       # اتصالات إضافية وقت الضغط
    pool_recycle=1800      # يعيد تدوير الاتصال كل 30 دقيقة لتفادي timeout
)

SessionLocal = sessionmaker(bind=engine, autoflush=False,
                            autocommit=False, future=True)

def with_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        session: Session = SessionLocal()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    return wrapper
