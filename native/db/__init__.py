import traceback

from config import db_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
engine = create_engine(
    f"mysql+pymysql://{db_config.user}:{db_config.passwd}@{db_config.host}:{db_config.port}/{db_config.db}?charset=utf8",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)
SessionFactory = sessionmaker(bind=engine)


def execute_select(sql):
    session = scoped_session(SessionFactory)
    results = []
    try:
        results = session.execute(sql).fetchall()
    except Exception as e:
        traceback.print_exc()
    finally:
        session.remove()
    return results


def execute_select_first(sql):
    session = scoped_session(SessionFactory)
    results = []
    try:
        results = session.execute(sql).first()
    except Exception as e:
        traceback.print_exc()
    finally:
        session.remove()
    return results


def execute_ins(sql):
    session = scoped_session(SessionFactory)
    try:
        session.execute(sql)
        session.commit()
    except Exception as e:
        traceback.print_exc()
    finally:
        session.remove()
