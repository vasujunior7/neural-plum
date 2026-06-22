# Neural Plum — Engineering Improvements & Updated User Flow

> **Document purpose**: What to build next, why it matters, how the user experience changes, and what the world's best AI claims companies are already doing that inspired these ideas.

---

## Table of Contents

1. [What the World's Best Are Doing](#1-what-the-worlds-best-are-doing)
2. [Four Core Improvements](#2-four-core-improvements)
3. [Updated System Architecture](#3-updated-system-architecture)
4. [Updated User Flow — Step by Step](#4-updated-user-flow--step-by-step)
5. [Implementation Priority](#5-implementation-priority)

---

## 1. What the World's Best Are Doing

Before building, understand who's already pushing the edge — and what specifically to steal from them.

---

### 🟡 Lemonade — AI Jim (USA)

**What they do**: Lemonade's AI Jim processes claims end-to-end from video submission to payout — no human required for most claims. It analyzes behavioral signals in the video (not just the words), cross-checks metadata, and either pays immediately or flags for human review.

**What to borrow for Neural Plum**:
- **Behavioral signal extraction** — not just *what* documents say, but *inconsistencies* across them (different handwriting styles, mismatched hospital logos, timestamps that don't match admission records).
- **Confidence-gated auto-approval** — if confidence is above a threshold, approve automatically. Below it, route to manual review. Neural Plum's current system is binary; it should be a spectrum.
- **Real-time fraud alerts** — Lemonade added proactive fraud notifications in 2025. Our pipeline should emit a fraud signal log visible in the frontend dashboard.

---

### 🔵 Shift Technology — Shift Claims (Paris/Boston)

**What they do**: Shift Claims launched in September 2025 as the most advanced agentic claims platform in the world. Their agents assess claim complexity, classify and prioritize claims, assist human handlers with dynamic guidance, and automate straight-through processing (STP) — all in one pipeline. Early adopters report 60% automation rate and 30% faster handling.

The key architectural insight from Shift's Chief Scientist Eric Sibony:
> *"Rules-based approaches struggle to handle the nuance and variability of most real-world cases... Agentic AI provides a powerful transformation tool that increases automation when appropriate and provides the right kind of advice when a human needs to be in the loop."*

**What to borrow for Neural Plum**:
- **Complexity scoring before routing** — before running all agents, score the claim's complexity (simple OPD vs. surgical with pre-auth). Route simple claims to fast-path STP. Route complex claims through all agents.
- **Human-in-the-loop guidance** — when a claim goes to `MANUAL_REVIEW`, the frontend should tell the human handler *exactly* what to check, not just flag it.
- **STP Agent concept** — a dedicated straight-through-processing path for clean, simple claims that don't need all 4 agents.

---

### 🟢 Accenture GenAI Claims Framework (Global Consulting Research)

**What they do**: Accenture's 2026 framework defines two tiers of agents: **Super Agents** (high-level orchestrators that handle intake, verification, adjudication, fraud) and **Utility Agents** (focused extractors and validators that feed data to Super Agents). This maps directly onto what Neural Plum *should* be.

**What to borrow for Neural Plum**:
- The **Supervisor** becomes a true Super Agent that reasons about the claim, not just sequences agents.
- Each existing agent (DocVerification, Extraction, FraudCheck, Decision) becomes a Utility Agent with a narrow, well-defined job.
- Add a **Case Summarization Agent** — after a decision is made, generate a plain-language summary for the claimant explaining what happened and why.

---

### 🟠 DSW UnifyAI / India InsurTech Leaders (India-specific)

**What they do**: Indian InsurTechs operating under IRDAI governance embed Explainable AI (XAI) from the ground up, attaching a "reason code" to every recommendation so every decision can be traced back to a specific policy clause, data source, or rule. This is not optional — IRDAI compliance requires it.

> *"By maintaining transparent decision logs, we can trace every recommendation back to the underlying factors and data sources."* — DSW UnifyAI CEO

**What to borrow for Neural Plum**:
- Every rejection, partial approval, or manual review flag must reference the specific policy section that triggered it (e.g., `policy §3.2 — 90-day waiting period for pre-existing conditions`).
- The frontend should render these as expandable "Why was my claim rejected?" sections.
- This is the single biggest differentiator for a Plum-specific submission — Plum operates in India under IRDAI.

---

## 2. Four Core Improvements

---

### Improvement 1 — Explainability Layer with Policy Clause References

**One-line summary**: Every decision maps to the exact policy section that caused it.

**What to build**:

Attach a `policy_reference` string to every rule check inside the `PolicyEngine`. Pass these references through to the final `ClaimDecision` response object.

```python
# Current (in policy engine)
if days_since_coverage < waiting_period_days:
    return Decision(status="REJECTED", reason="Waiting period not met")

# Improved
if days_since_coverage < waiting_period_days:
    return Decision(
        status="REJECTED",
        reason="Waiting period not met",
        policy_reference="policy_terms.json § waiting_periods.diabetes — 90 days required, {days_since_coverage} days elapsed",
        human_explanation="Your policy requires 90 days of active coverage before diabetes-related claims are eligible. Your coverage started {coverage_start_date}, and this claim was submitted only {days_since_coverage} days later."
    )
```

**Add to the response schema** (`models.py`):

```python
class DecisionRationale(BaseModel):
    rule_triggered: str          # e.g. "waiting_period_check"
    policy_reference: str        # e.g. "§3.2 waiting_periods.diabetes"
    computed_value: str          # e.g. "45 days elapsed"
    threshold_value: str         # e.g. "90 days required"
    human_explanation: str       # Plain English, claimant-facing

class ClaimDecision(BaseModel):
    # ... existing fields ...
    rationale: list[DecisionRationale]   # NEW
```

**Frontend change**: Add a collapsible "Decision Breakdown" panel on the claim detail page that shows each rationale entry as a human-readable card.

**Why this wins**: IRDAI compliance. No other assignment submission will have this. It takes 3-4 hours of focused work and zero extra LLM calls.

---

### Improvement 2 — Confidence-Calibrated Extraction with Per-Field Uncertainty

**One-line summary**: Instead of binary extraction success/failure, emit a confidence score per extracted field and route uncertain claims intelligently.

**What to build**:

Change the extraction prompt to return per-field confidence alongside values:

```python
EXTRACTION_PROMPT = """
Extract the following fields from the medical document.
For each field, return a JSON object with:
  - "value": the extracted value
  - "confidence": float between 0.0 and 1.0
  - "source_span": the exact text from the document that supports this value

If a field cannot be found, set confidence to 0.0 and value to null.

Fields to extract: patient_name, diagnosis_code, hospital_name, 
admission_date, discharge_date, total_amount, doctor_name, 
procedure_description

Return ONLY valid JSON, no preamble.
"""
```

**Add a confidence routing rule** in the Supervisor:

```python
LOW_CONFIDENCE_THRESHOLD = 0.6

uncertain_fields = [
    f for f, data in extracted.items() 
    if data["confidence"] < LOW_CONFIDENCE_THRESHOLD
]

if len(uncertain_fields) > 2:
    return ClaimDecision(status="NEEDS_REUPLOAD", 
                         reason=f"Low confidence on: {uncertain_fields}")
elif len(uncertain_fields) > 0:
    # Proceed but reduce overall confidence score
    claim.confidence_score -= 0.1 * len(uncertain_fields)
```

**Why this wins**: Real Indian medical documents (hand-stamped discharge summaries, bilingual forms, photocopies) fail silently in the current system. This makes failures visible, auditable, and actionable.

---

### Improvement 3 — Semantic Fraud Reasoning Agent

**One-line summary**: Replace the single frequency-check fraud rule with an LLM that reasons across all extracted fields for semantic inconsistencies.

**What to build**:

Add a second fraud-check step *after* extraction that uses the LLM to read the full structured claim:

```python
FRAUD_REASONING_PROMPT = """
You are an insurance fraud analyst reviewing a health insurance claim in India.
Analyze the following structured claim data and identify semantic red flags.

Claim data:
{claim_json}

Check for:
1. Procedure-diagnosis mismatch (e.g., MRI billed for a cold)
2. Amount outliers vs. typical Indian hospital rates for this procedure
3. Admission/discharge date inconsistencies
4. Doctor credentials mismatched with procedure type
5. Hospital name inconsistencies across documents

Return a JSON object:
{
  "fraud_score": 0.0-1.0,
  "flags": [
    {
      "signal": "description of the red flag",
      "severity": "low|medium|high",
      "fields_involved": ["field1", "field2"]
    }
  ],
  "recommendation": "APPROVE | MANUAL_REVIEW | REJECT"
}
"""
```

**Routing logic**:

```python
if fraud_result.fraud_score > 0.8:
    decision = "MANUAL_REVIEW"
    confidence_penalty = 0.3
elif fraud_result.fraud_score > 0.5:
    decision = "MANUAL_REVIEW"  
    confidence_penalty = 0.15
# fraud_score below 0.5 = proceed normally
```

**Important**: This agent is *advisory only* — it raises `MANUAL_REVIEW` probability, it never auto-rejects. This avoids false positives.

**Why this wins**: The current fraud agent catches one pattern. This catches the patterns that actually matter in Indian health insurance — procedure-diagnosis mismatches, rate outliers, and document cross-inconsistencies.

---

### Improvement 4 — Dynamic Claim Routing via a Planner Agent

**One-line summary**: Before running any agents, classify the claim type and decide which agents to run, in what order, skipping unnecessary ones.

**What to build**:

Add a `PlannerAgent` that produces a `ClaimPlan` before the pipeline starts:

```python
class ClaimPlan(BaseModel):
    claim_category: str          # "OPD" | "IPD" | "DENTAL" | "MATERNITY" | "SURGICAL"
    complexity_score: float      # 0.0-1.0
    agents_to_run: list[str]     # e.g. ["DocVerification", "Extraction", "Decision"]
    agents_to_skip: dict[str, str]  # agent_name -> reason for skipping
    fast_track: bool             # True = simple claim, skip fraud check

ROUTING_TABLE = {
    "OPD": {
        "agents_to_run": ["DocVerification", "Extraction", "Decision"],
        "skip": {"FraudCheck": "OPD claims below ₹5000 are low-risk; skip fraud for speed"},
        "fast_track": True
    },
    "SURGICAL": {
        "agents_to_run": ["DocVerification", "Extraction", "FraudCheck", "SemanticFraud", "Decision"],
        "skip": {},
        "fast_track": False
    },
    "DENTAL": {
        "agents_to_run": ["DocVerification", "Extraction", "Decision"],
        "skip": {"FraudCheck": "Dental claims processed under separate sub-limit rules"},
        "fast_track": True
    }
}
```

**Why this wins**: Architecturally, this is the difference between a scripted pipeline and an intelligent system. It also directly mirrors what Shift Technology's "assess and prioritize" step does — score complexity before routing. It makes the system faster for simple claims and more thorough for complex ones.

---

## 3. Updated System Architecture

```
                         ┌─────────────────────────────────────────┐
                         │           CLAIM SUBMISSION               │
                         │  { documents, member_id, claim_type }   │
                         └──────────────────┬──────────────────────┘
                                            │
                                            ▼
                         ┌─────────────────────────────────────────┐
                         │         PLANNER AGENT  [NEW]            │
                         │  • Classifies claim type                │
                         │  • Scores complexity (0.0–1.0)          │
                         │  • Emits ClaimPlan (which agents to run) │
                         └──────────────────┬──────────────────────┘
                                            │
                              ┌─────────────┴──────────────┐
                              │                            │
                        Fast Track                   Full Pipeline
                     (OPD, Dental, low ₹)        (Surgical, IPD, high ₹)
                              │                            │
                              ▼                            ▼
              ┌───────────────────────┐    ┌───────────────────────────┐
              │  DOC VERIFICATION     │    │   DOC VERIFICATION        │
              │  Agent (unchanged)    │    │   Agent (unchanged)       │
              └──────────┬────────────┘    └────────────┬──────────────┘
                         │                              │
                         ▼                              ▼
              ┌───────────────────────┐    ┌───────────────────────────┐
              │  EXTRACTION Agent     │    │   EXTRACTION Agent        │
              │  + Per-field          │    │   + Per-field             │
              │    confidence  [NEW]  │    │     confidence  [NEW]     │
              └──────────┬────────────┘    └────────────┬──────────────┘
                         │                              │
                         │                              ▼
                         │               ┌───────────────────────────┐
                         │               │  FRAUD CHECK Agent        │
                         │               │  (frequency rules)        │
                         │               └────────────┬──────────────┘
                         │                            │
                         │                            ▼
                         │               ┌───────────────────────────┐
                         │               │  SEMANTIC FRAUD Agent     │
                         │               │  LLM reasoning across     │
                         │               │  all fields  [NEW]        │
                         │               └────────────┬──────────────┘
                         │                            │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────────────────┐
                         │         DECISION Agent (PolicyEngine)   │
                         │  + Rationale with policy references[NEW]│
                         └──────────────────┬──────────────────────┘
                                            │
                                            ▼
                         ┌─────────────────────────────────────────┐
                         │         CASE SUMMARY Agent  [NEW]       │
                         │  Generates plain-language explanation   │
                         │  for claimant (approved/rejected/why)   │
                         └──────────────────┬──────────────────────┘
                                            │
                                            ▼
                         ┌─────────────────────────────────────────┐
                         │         FINAL RESPONSE                  │
                         │  status | amount | rationale[] |        │
                         │  confidence | policy_references |       │
                         │  human_summary | fraud_flags            │
                         └─────────────────────────────────────────┘
```

---

## 4. Updated User Flow — Step by Step

### Old Flow (what exists today)

```
User uploads docs → Fixed 4-agent pipeline runs → 
APPROVED / REJECTED / MANUAL_REVIEW returned → 
Frontend shows status code + confidence score
```

### New Flow (what it becomes)

---

**Step 1 — Claim Submission (unchanged UI)**

User submits a claim with documents and member details via the React frontend. No change here.

---

**Step 2 — Instant Classification (new, ~0.5s)**

The Planner Agent classifies the claim within milliseconds using the `claim_type` field and estimated amount. The frontend can show this immediately:

```
⚡ Claim classified: OPD Consultation — Fast Track eligible
   Estimated processing: ~3 seconds
```

---

**Step 3 — Document Verification (existing, improved feedback)**

Documents are checked. If a document fails, instead of just `NEEDS_REUPLOAD`, the response now includes:

```
❌ Document rejected: Hospital discharge summary appears to belong to a 
   different patient (patient name on Page 1 does not match member roster).
   → Please re-upload the correct document for: Priya Sharma (Member ID: PLM-0042)
```

---

**Step 4 — Confidence-Calibrated Extraction (improved)**

The extraction agent now shows per-field confidence in the Langfuse trace (and optionally in the frontend for MANUAL_REVIEW cases):

```
✅ patient_name: "Priya Sharma"       [confidence: 0.97]
✅ diagnosis_code: "J18.9"            [confidence: 0.91]
⚠️  admission_date: "12/03/2024"      [confidence: 0.61]  ← flagged
✅ total_amount: ₹24,500              [confidence: 0.94]
```

If 2+ fields fall below 0.6, the claim is paused and the user is asked to re-confirm those specific fields rather than re-uploading everything.

---

**Step 5 — Semantic Fraud Reasoning (new, surgical/IPD claims only)**

The LLM fraud agent silently reviews the full extracted claim. If it finds flags, they appear in the internal audit log and influence the confidence score:

```
[FRAUD AGENT] Score: 0.34 — Low risk
  → No significant anomalies detected
  → Procedure (chest X-ray) is consistent with diagnosis (pneumonia)
  → Amount (₹24,500) is within normal range for this procedure in Tier-2 hospitals
```

For a suspicious claim:

```
[FRAUD AGENT] Score: 0.71 — Elevated risk → MANUAL_REVIEW
  ⚠ Flag: MRI billing (₹45,000) inconsistent with admitting diagnosis (common cold)
  ⚠ Flag: Admission date (Sunday) unusual for elective imaging in this hospital network
```

---

**Step 6 — Policy Decision with Rationale (improved)**

The Decision Agent now returns full rationale, not just a status code.

**Before**:
```json
{ "status": "REJECTED", "reason": "Waiting period not met" }
```

**After**:
```json
{
  "status": "REJECTED",
  "rationale": [
    {
      "rule_triggered": "waiting_period_check",
      "policy_reference": "policy_terms.json § waiting_periods.diabetes",
      "computed_value": "45 days elapsed since coverage start",
      "threshold_value": "90 days required for diabetes-related claims",
      "human_explanation": "Your policy requires 90 days of active coverage before diabetes-related claims are eligible. Your coverage started on Jan 15, 2024, but this claim was filed only 45 days later on Mar 1, 2024. You will be eligible to file this type of claim from April 15, 2024."
    }
  ]
}
```

---

**Step 7 — Case Summary (new)**

A final lightweight LLM call generates a claimant-facing plain-language summary:

> **Your claim has been partially approved.**
>
> We reviewed your dental claim for ₹18,500 submitted on March 12, 2024.
>
> ✅ **Approved**: Root canal treatment — ₹12,000 (after 10% copay: **₹10,800 payable**)
> ❌ **Not covered**: Teeth whitening — ₹6,500 (cosmetic procedures are excluded under §5.1 of your policy)
>
> Expected payout within 3–5 business days to your registered bank account.

This goes directly into the frontend claim detail view.

---

**Step 8 — Manual Review Guidance (new, for MANUAL_REVIEW cases)**

When a claim goes to `MANUAL_REVIEW`, the response now includes a handler checklist:

```
🔍 Manual Review Required — Handler Checklist:

1. Verify admission date on Page 2 of discharge summary (low extraction confidence: 0.61)
2. Confirm pre-authorization reference number for MRI (required for amounts > ₹10,000)
3. Review fraud flag: MRI billing inconsistency with diagnosis (fraud score: 0.71)

Estimated review time: 15 minutes
```

---

## 5. Implementation Priority

| # | Improvement | Engineering Effort | Impact on Assignment Score | Do This First? |
|---|---|---|---|---|
| 1 | Explainability + Policy References | Low (3–4 hrs) | ⭐⭐⭐⭐⭐ Highest | ✅ Yes |
| 2 | Confidence-Calibrated Extraction | Medium (5–6 hrs) | ⭐⭐⭐⭐ High | ✅ Yes |
| 3 | Semantic Fraud Reasoning Agent | Medium (4–5 hrs) | ⭐⭐⭐⭐ High | If time allows |
| 4 | Planner Agent + Dynamic Routing | High (8–10 hrs) | ⭐⭐⭐ Medium-High | If time allows |
| 5 | Case Summary Agent | Low (2 hrs) | ⭐⭐⭐ Medium | Nice to have |
| 6 | Manual Review Handler Checklist | Low (2–3 hrs) | ⭐⭐⭐ Medium | Nice to have |

---

### The Single Most Important Addition

**Do the Explainability Layer first, no question.**

Every other team submitting this assignment will have 4 agents and 12 passing tests. Yours will be the only pipeline that tells the reviewer *exactly which line of the policy document* caused every rejection — the same thing IRDAI requires, the same thing DSW UnifyAI and Bajaj Allianz are building in production, and the same thing Shift Technology's Chief Scientist calls "the right kind of advice when a human needs to be in the loop."

That's the delta worth building.

---

*Document generated for Neural Plum — Plum AI Engineer Assignment. Inspired by Lemonade AI Jim, Shift Technology Shift Claims, Accenture GenAI Claims Framework, and IRDAI-compliant Indian InsurTech practices.*
