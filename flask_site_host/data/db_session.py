import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return
    conn_str = os.getenv("MYSQL")
    # 'mysql://b38x72no83ne2fwf36qa:pscale_pw_nLy88xduCtUXA1mSjyeUdpHIVSv3pWKr2di52mkhtJA@aws.connect.psdb.cloud/gadukadatabase?ssl={"rejectUnauthorized":true}'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, connect_args={'charset':'utf8mb4'}, pool_recycle=3600)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
