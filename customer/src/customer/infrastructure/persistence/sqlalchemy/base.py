from sqlalchemy.orm import DeclarativeBase


class CustomerBase(DeclarativeBase):
    """Metadata isolated from other installable business modules."""
