from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig

class DocumentVerificationAgent(BaseAgent):
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        notes = []
        # Check required documents
        doc_reqs = policy.document_requirements.get(claim.claim_category.value.upper())
        if not doc_reqs:
            doc_reqs = policy.document_requirements.get(claim.claim_category.value.lower())
            
        required_types = doc_reqs.required if doc_reqs else []
        provided_types = [doc.actual_type for doc in claim.documents if doc.actual_type]
        
        missing = [rt for rt in required_types if rt not in provided_types]
        if missing:
            notes.append(f"Missing required documents: {', '.join(missing)}. Uploaded: {', '.join(provided_types)}")
            return AgentResult(passed=False, confidence=1.0, notes=notes, rejection_reasons=["MISSING_DOCUMENTS"])
            
        # Check readability
        for doc in claim.documents:
            if doc.quality == "UNREADABLE":
                notes.append(f"Document {doc.file_name} is unreadable. Please re-upload.")
                return AgentResult(passed=False, confidence=1.0, notes=notes, rejection_reasons=["UNREADABLE_DOCUMENT"])
                
        # Check patient names match
        patient_names = set()
        for doc in claim.documents:
            if doc.patient_name_on_doc:
                patient_names.add(doc.patient_name_on_doc)
            elif doc.content and "patient_name" in doc.content:
                patient_names.add(doc.content["patient_name"])
                
        if len(patient_names) > 1:
            names_str = " and ".join(patient_names)
            notes.append(f"Patient names mismatch across documents: found {names_str}.")
            return AgentResult(passed=False, confidence=1.0, notes=notes, rejection_reasons=["PATIENT_NAME_MISMATCH"])
            
        return AgentResult(passed=True, confidence=1.0, notes=["All documents verified successfully."])
