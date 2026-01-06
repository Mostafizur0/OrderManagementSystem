from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
)


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate table names by converting the class name
        to lowercase.
        """
        return cls.__name__.lower()

    @declared_attr
    def __table_args__(cls):
        """
        Specify default table arguments, like schema, if needed.
        """
        return {"schema": "public"}
