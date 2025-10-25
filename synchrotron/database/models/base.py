from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class PersistentBase(MappedAsDataclass, DeclarativeBase):
    pass
