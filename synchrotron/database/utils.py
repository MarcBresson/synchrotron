from contextlib import contextmanager
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.configurations import SQLAlchemyDBConfig


@cache
def get_engine():
    db_config = SQLAlchemyDBConfig.get()
    engine = create_engine(
        str(db_config.engine_url), **db_config.engine_options.model_dump()
    )
    # ensure tables are created
    create_db(engine)
    return engine


@contextmanager
def session_manager(*, autocommit: bool = False):
    engine = get_engine()

    with Session(engine, expire_on_commit=False) as session:
        yield session

        if autocommit:
            session.commit()


def create_db(engine):
    """Create the database tables."""
    from .models.base import PersistentBase

    PersistentBase.metadata.create_all(engine)
