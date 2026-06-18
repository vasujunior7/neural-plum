from fastapi import APIRouter, Depends, HTTPException, Security, Form, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..db_models import DBClaim
from ..models import ClaimSubmission, ClaimCategory, DocumentInput
import base64
from datetime import datetime
from typing import List
from ..policy.loader import get_policy
from ..agents.supervisor import Supervisor
from ..tracing.logger import TraceLogger
from ..auth import verify_api_key

router = APIRouter(prefix="/v1/claims", tags=["claims"])

@router.post("")
async def submit_claim(
    member_id: str = Form(...),
    claim_category: str = Form(...),
    claimed_amount: float = Form(...),
    documents: List[UploadFile] = File(...),
    db: Session = Depends(get_db), 
    api_key: str = Security(verify_api_key)
):
    docs = []
    for doc in documents:
        content_bytes = await doc.read()
        b64_content = base64.b64encode(content_bytes).decode('utf-8')
        
        # Infer actual_type from filename to satisfy the DocumentVerificationAgent
        fn_upper = doc.filename.upper()
        actual_type = None
        if "PRESCRIPTION" in fn_upper:
            actual_type = "PRESCRIPTION"
        elif "BILL" in fn_upper or "RECEIPT" in fn_upper:
            actual_type = "HOSPITAL_BILL"
        elif "REPORT" in fn_upper or "LAB" in fn_upper:
            actual_type = "LAB_REPORT"

        docs.append(DocumentInput(
            file_id=doc.filename,
            file_name=doc.filename,
            actual_type=actual_type,
            content={"mime_type": doc.content_type, "data": b64_content}
        ))

    claim = ClaimSubmission(
        member_id=member_id,
        policy_id="POL-001",
        claim_category=ClaimCategory(claim_category),
        treatment_date=datetime.now().strftime("%Y-%m-%d"),
        claimed_amount=claimed_amount,
        documents=docs
    )

    policy = get_policy()
    supervisor = Supervisor(policy)
    
    output = supervisor.process_claim(claim)
    
    db_claim = DBClaim(
        member_id=claim.member_id,
        claim_category=claim.claim_category.value,
        claimed_amount=claim.claimed_amount,
        status=output["final_state"],
        decision=output.get("decision"),
        approved_amount=output.get("approved_amount"),
        rejection_reasons=output.get("rejection_reasons"),
        notes=output.get("notes"),
        confidence=output.get("confidence")
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    
    trace_logger = TraceLogger(db)
    trace_logger.log_trace(db_claim.id, output.get("traces", []))
    
    return {
        "claim_id": db_claim.id,
        "status": output["final_state"],
        "decision": output.get("decision"),
        "approved_amount": output.get("approved_amount"),
        "rejection_reasons": output.get("rejection_reasons"),
        "notes": output.get("notes"),
        "confidence": output.get("confidence"),
        "traces": output.get("traces")
    }

@router.get("/{claim_id}")
def get_claim(claim_id: int, db: Session = Depends(get_db), api_key: str = Security(verify_api_key)):
    claim = db.query(DBClaim).filter(DBClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    from ..db_models import DBTrace
    traces = db.query(DBTrace).filter(DBTrace.claim_id == claim_id).order_by(DBTrace.id.asc()).all()
    trace_list = []
    for t in traces:
        # Ensure we send the format {step, status, message} expected by the frontend
        status = 'INFO'
        message = str(t.result)
        if isinstance(t.result, dict):
            status = 'PASS' if t.result.get('passed', True) else 'FAIL'
            notes = t.result.get('notes', [])
            rejection_reasons = t.result.get('rejection_reasons', [])
            all_msgs = notes + rejection_reasons
            if all_msgs:
                message = "; ".join(all_msgs)
            else:
                message = "Completed check."

        trace_list.append({
            "step": t.state,
            "status": status,
            "message": message
        })

    reason = ""
    if claim.rejection_reasons:
        reason = "; ".join(claim.rejection_reasons)
    elif claim.notes:
        reason = "; ".join(claim.notes)

    return {
        "id": claim.id,
        "member_id": claim.member_id,
        "status": claim.status,
        "decision": claim.decision,
        "claimed_amount": claim.claimed_amount,
        "approved_amount": claim.approved_amount,
        "claim_category": claim.claim_category,
        "confidence": claim.confidence,
        "reason": reason,
        "trace": trace_list,
        "extracted_data": {}
    }

@router.get("")
def list_claims(db: Session = Depends(get_db), api_key: str = Security(verify_api_key)):
    claims = db.query(DBClaim).order_by(DBClaim.id.desc()).limit(50).all()
    return [
        {
            "id": claim.id,
            "member_id": claim.member_id,
            "claim_category": claim.claim_category,
            "status": claim.status,
            "decision": claim.decision,
            "claimed_amount": claim.claimed_amount,
            "approved_amount": claim.approved_amount,
            "confidence": claim.confidence
        }
        for claim in claims
    ]

@router.delete("")
def delete_all_claims(db: Session = Depends(get_db), api_key: str = Security(verify_api_key)):
    from ..db_models import DBTrace
    db.query(DBTrace).delete()
    db.query(DBClaim).delete()
    db.commit()
    return {"message": "All claims deleted successfully"}
