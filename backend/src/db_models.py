from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class DBClaim(Base):
    __tablename__ = "claims"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, index=True)
    claim_category = Column(String)
    claimed_amount = Column(Float)
    status = Column(String)
    decision = Column(String, nullable=True)
    approved_amount = Column(Float, nullable=True)
    rejection_reasons = Column(JSON, nullable=True)
    notes = Column(JSON, nullable=True)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBTrace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, index=True)
    state = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
