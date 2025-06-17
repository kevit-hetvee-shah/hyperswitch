from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Merchant(Base):
    id: str = Column(Integer, primary_key=True)
    merchant_id: str = Column(String, unique=True)


class APIKeys(Base):
    id: str = Column(Integer, primary_key=True)
    merchant_id = Column(String, ForeignKey(Merchant.merchant_id))
    merchant = relationship("Merchant", back_populates="api_keys")
    api_key = Column(String, unique=True)
    key_id = Column(String, unique=True)
