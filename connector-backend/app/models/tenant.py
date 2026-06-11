from sqlalchemy import Column, Integer, String
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)