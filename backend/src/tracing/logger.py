from sqlalchemy.orm import Session
from ..db_models import DBTrace
import os

class TraceLogger:
    def __init__(self, db: Session):
        self.db = db
                
    def log_trace(self, claim_id: int, traces: list):
        for trace in traces:
            db_trace = DBTrace(
                claim_id=claim_id,
                state=trace["state"],
                result=trace["result"]
            )
            self.db.add(db_trace)
            
        self.db.commit()
