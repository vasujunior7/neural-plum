from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class ClaimCategory(str, Enum):
    CONSULTATION = "CONSULTATION"
    DIAGNOSTIC = "DIAGNOSTIC"
    PHARMACY = "PHARMACY"
    DENTAL = "DENTAL"
    VISION = "VISION"
    ALTERNATIVE_MEDICINE = "ALTERNATIVE_MEDICINE"

class DocumentType(str, Enum):
    PRESCRIPTION = "PRESCRIPTION"
    HOSPITAL_BILL = "HOSPITAL_BILL"
    LAB_REPORT = "LAB_REPORT"
    DIAGNOSTIC_REPORT = "DIAGNOSTIC_REPORT"
    PHARMACY_BILL = "PHARMACY_BILL"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    DENTAL_REPORT = "DENTAL_REPORT"

class DecisionType(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"

class ClaimState(str, Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    VERIFYING = "VERIFYING"
    EXTRACTING = "EXTRACTING"
    ADJUDICATING = "ADJUDICATING"
    FRAUD_CHECKING = "FRAUD_CHECKING"
    SEMANTIC_FRAUD = "SEMANTIC_FRAUD"
    DECIDING = "DECIDING"
    SUMMARIZING = "SUMMARIZING"
    DONE = "DONE"

class DocumentInput(BaseModel):
    file_id: str
    file_name: Optional[str] = None
    actual_type: Optional[str] = None
    quality: Optional[str] = None
    patient_name_on_doc: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

class ClaimHistory(BaseModel):
    claim_id: str
    date: str
    amount: float
    provider: str

class ClaimSubmission(BaseModel):
    member_id: str
    policy_id: str
    claim_category: ClaimCategory
    treatment_date: str
    claimed_amount: float
    ytd_claims_amount: float = 0.0
    ytd_alternative_sessions: int = 0
    hospital_name: Optional[str] = None
    documents: List[DocumentInput]
    claims_history: Optional[List[ClaimHistory]] = None
    simulate_component_failure: Optional[bool] = False

# Policy models for loader
class PolicyHolder(BaseModel):
    company_name: str
    employee_count: int
    policy_start_date: str
    policy_end_date: str
    renewal_status: str

class FamilyFloater(BaseModel):
    enabled: bool
    combined_limit: float
    covered_relationships: List[str]

class Coverage(BaseModel):
    sum_insured_per_employee: float
    annual_opd_limit: float
    per_claim_limit: float
    family_floater: FamilyFloater

class OPDCategoryDetails(BaseModel):
    sub_limit: float
    copay_percent: float
    network_discount_percent: Optional[float] = 0.0
    requires_prescription: bool
    requires_pre_auth: Optional[bool] = False
    covered: bool
    pre_auth_threshold: Optional[float] = None
    high_value_tests_requiring_pre_auth: Optional[List[str]] = None
    branded_drug_copay_percent: Optional[float] = None
    generic_mandatory: Optional[bool] = None
    requires_dental_report: Optional[bool] = None
    covered_procedures: Optional[List[str]] = None
    excluded_procedures: Optional[List[str]] = None
    covered_items: Optional[List[str]] = None
    excluded_items: Optional[List[str]] = None
    requires_registered_practitioner: Optional[bool] = None
    max_sessions_per_year: Optional[int] = None
    covered_systems: Optional[List[str]] = None

class WaitingPeriods(BaseModel):
    initial_waiting_period_days: int
    pre_existing_conditions_days: int
    specific_conditions: Dict[str, int]

class Exclusions(BaseModel):
    conditions: List[str]
    dental_exclusions: List[str]
    vision_exclusions: List[str]

class PreAuthorization(BaseModel):
    required_for: List[str]
    validity_days: int

class SubmissionRules(BaseModel):
    deadline_days_from_treatment: int
    minimum_claim_amount: float
    currency: str

class DocRequirement(BaseModel):
    required: List[str]
    optional: List[str]

class FraudThresholds(BaseModel):
    same_day_claims_limit: int
    monthly_claims_limit: int
    high_value_claim_threshold: float
    auto_manual_review_above: float
    fraud_score_manual_review_threshold: float

class MemberInfo(BaseModel):
    member_id: str
    name: str
    date_of_birth: str
    gender: str
    relationship: str
    join_date: Optional[str] = None
    dependents: Optional[List[str]] = None
    primary_member_id: Optional[str] = None

class PolicyConfig(BaseModel):
    policy_id: str
    policy_name: str
    insurer: str
    policy_holder: PolicyHolder
    coverage: Coverage
    opd_categories: Dict[str, OPDCategoryDetails]
    waiting_periods: WaitingPeriods
    exclusions: Exclusions
    pre_authorization: PreAuthorization
    network_hospitals: List[str]
    submission_rules: SubmissionRules
    document_requirements: Dict[str, DocRequirement]
    fraud_thresholds: FraudThresholds
    members: List[MemberInfo]

# --- Phase 1: Explainability Layer ---
class DecisionRationale(BaseModel):
    rule_triggered: str          # e.g. "waiting_period_check"
    policy_reference: str        # e.g. "§ waiting_periods.diabetes"
    computed_value: str          # e.g. "45 days elapsed"
    threshold_value: str         # e.g. "90 days required"
    human_explanation: str       # Plain English, claimant-facing

# --- Phase 2: Confidence-Calibrated Extraction ---
class ExtractedField(BaseModel):
    value: Optional[Any] = None
    confidence: float = 1.0
    source_span: Optional[str] = None

# --- Phase 3: Semantic Fraud ---
class FraudFlag(BaseModel):
    signal: str
    severity: str  # "low" | "medium" | "high"
    fields_involved: List[str] = Field(default_factory=list)

class SemanticFraudResult(BaseModel):
    fraud_score: float = 0.0
    flags: List[FraudFlag] = Field(default_factory=list)
    recommendation: str = "APPROVE"  # "APPROVE" | "MANUAL_REVIEW" | "REJECT"

# --- Phase 4: Planner Agent ---
class ClaimPlan(BaseModel):
    claim_category: str = ""
    complexity_score: float = 0.5
    agents_to_run: List[str] = Field(default_factory=list)
    agents_to_skip: Dict[str, str] = Field(default_factory=dict)
    fast_track: bool = False

# --- Phase 6: Manual Review Checklist ---
class ChecklistItem(BaseModel):
    priority: int           # 1 = highest
    action: str             # what to verify
    reason: str             # why it needs review
    source_agent: str       # which agent flagged it
    estimated_minutes: int  # how long this check takes

class ManualReviewChecklist(BaseModel):
    items: List[ChecklistItem] = Field(default_factory=list)
    total_estimated_minutes: int = 0

# Agent Result Base
class AgentResult(BaseModel):
    passed: bool
    confidence: float
    notes: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)
    decision: Optional[DecisionType] = None
    approved_amount: Optional[float] = None
    rationale: List[DecisionRationale] = Field(default_factory=list)

# Check Result (Deterministic Rules)
class LineItemAdjudication(BaseModel):
    description: str
    claimed_amount: float
    approved_amount: float
    rejected_amount: float
    rejection_reason: Optional[str] = None

class CheckResult(BaseModel):
    passed: bool
    rejection_reasons: List[str] = Field(default_factory=list)
    approved_amount: Optional[float] = None
    line_items: List[LineItemAdjudication] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    rationale: List[DecisionRationale] = Field(default_factory=list)
