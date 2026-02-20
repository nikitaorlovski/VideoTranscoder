from sqlalchemy import Integer, String, LargeBinary, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from app.database.db import Base

class UserOrm(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[bytes] = mapped_column(LargeBinary)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')