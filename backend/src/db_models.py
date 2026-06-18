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
    rationale = Column(JSON, nullable=True)
    field_confidences = Column(JSON, nullable=True)
    semantic_fraud_result = Column(JSON, nullable=True)
    claim_plan = Column(JSON, nullable=True)
    human_summary = Column(String, nullable=True)
    handler_checklist = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBTrace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, index=True)
    state = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

