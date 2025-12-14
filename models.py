from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    password = Column(String)
    wallet = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
