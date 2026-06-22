# 🚀 Neural Plum — Evaluation Report (EVAL_REPORT.md)

This document serves as the formal evaluation report verifying the system's behavior across the 12 deterministic test cases specified in the assignment.

**Final Score:** 12 / 12 Passed (100% Match)

---

## ✅ TC001: Wrong Document Uploaded
* **Input:** Claim submitted with two `PRESCRIPTION` documents but missing the `HOSPITAL_BILL`.
* **Expected Decision:** EARLY_STOP (State: VERIFYING)
* **Actual Decision:** `VERIFYING` state with rejection reason `MISSING_DOCUMENTS`.
* **Match:** ✅ Yes
* **Explanation:** The `DocumentVerificationAgent` correctly cross-checks the uploaded document types against `policy_terms.json` requirements and safely halts execution before any LLM calls are made.

## ✅ TC002: Unreadable Document
* **Input:** Valid prescription but a blurry, unreadable pharmacy bill.
* **Expected Decision:** NEEDS_REUPLOAD / EARLY_STOP (State: VERIFYING)
* **Actual Decision:** `VERIFYING` state with rejection reason `UNREADABLE_DOCUMENT`.
* **Match:** ✅ Yes
* **Explanation:** The verification stage detects the unreadable status and requests re-upload specifically for the blurry document.

## ✅ TC003: Documents Belong to Different Patients
* **Input:** Prescription for 'Rajesh Kumar', Hospital Bill for 'Arjun Mehta'.
* **Expected Decision:** EARLY_STOP (State: VERIFYING)
* **Actual Decision:** `VERIFYING` state with rejection reason `PATIENT_NAME_MISMATCH`.
* **Match:** ✅ Yes
* **Explanation:** The verification agent successfully detects the cross-patient mismatch and securely aborts the claim.

## ✅ TC004: Clean Consultation — Full Approval
* **Input:** Complete, valid claim with valid member, covered treatment, ₹1,500 total.
* **Expected Decision:** APPROVED (₹1350)
* **Actual Decision:** `APPROVED` for ₹1350.0.
* **Match:** ✅ Yes
* **Explanation:** The PolicyEngine applies the mandatory 10% copay on consultation (₹1500 - ₹150 = ₹1350).

## ✅ TC005: Waiting Period — Diabetes
* **Input:** Member joined 2024-09-01. Claims for diabetes treatment on 2024-10-15 (within 90 days).
* **Expected Decision:** REJECTED (Reason: WAITING_PERIOD)
* **Actual Decision:** `REJECTED` with reason `WAITING_PERIOD`.
* **Match:** ✅ Yes
* **Explanation:** PolicyEngine strictly computes dates mathematically. `2024-09-01` + 90 days = `2024-11-29`. Since the treatment was `2024-10-15`, it correctly rejects the claim.

## ✅ TC006: Dental Partial Approval — Cosmetic Exclusion
* **Input:** Bill includes root canal (covered) and teeth whitening (cosmetic exclusion).
* **Expected Decision:** PARTIAL (₹8000)
* **Actual Decision:** `PARTIAL` for ₹8000.0.
* **Match:** ✅ Yes
* **Explanation:** The `adjudicate_line_items` process evaluates the specific items iteratively, excluding the cosmetic line item securely.

## ✅ TC007: MRI Without Pre-Authorization
* **Input:** MRI scan costing ₹15,000 without pre-authorization. (Policy requires pre-auth > ₹10,000).
* **Expected Decision:** REJECTED (Reason: PRE_AUTH_MISSING)
* **Actual Decision:** `REJECTED` with reason `PRE_AUTH_MISSING`.
* **Match:** ✅ Yes
* **Explanation:** The deterministic logic flags that MRI scan limits strictly dictate a rejection due to the missing boolean flag.

## ✅ TC008: Per-Claim Limit Exceeded
* **Input:** Claimed amount of ₹7,500. Per-claim limit is ₹5,000.
* **Expected Decision:** REJECTED (Reason: PER_CLAIM_EXCEEDED)
* **Actual Decision:** `REJECTED` with reason `PER_CLAIM_EXCEEDED`.
* **Match:** ✅ Yes
* **Explanation:** System strictly enforces the absolute caps defined in `policy_terms.json`.

## ✅ TC009: Fraud Signal — Multiple Same-Day Claims
* **Input:** 4th claim from the same member on the same day (Limit is 2).
* **Expected Decision:** MANUAL_REVIEW
* **Actual Decision:** `MANUAL_REVIEW` flagged at the `FRAUD_CHECKING` stage.
* **Match:** ✅ Yes
* **Explanation:** Instead of an automated rejection (which risks false positives), the fraud rules flag it securely to trigger an analyst's review.

## ✅ TC010: Network Hospital — Discount Applied
* **Input:** Valid claim at Apollo Hospitals (network hospital). ₹4500.
* **Expected Decision:** APPROVED (₹3240)
* **Actual Decision:** `APPROVED` for ₹3240.0.
* **Match:** ✅ Yes
* **Explanation:** The exact ordering matters. The system applies the 20% network discount first (₹4500 -> ₹3600), and *then* the 10% copay (₹3600 -> ₹3240).

## ✅ TC011: Component Failure — Graceful Degradation
* **Input:** Simulate mid-processing component timeout (Fraud Agent fails).
* **Expected Decision:** APPROVED (degraded confidence)
* **Actual Decision:** `APPROVED` for ₹4000.0, with a confidence dropped to **80.0%**.
* **Match:** ✅ Yes
* **Explanation:** We utilize the Multiplicative Confidence equation. The component failure drops the fraud multiplier strictly to 0.5 without hard-crashing the backend pipeline.

## ✅ TC012: Excluded Treatment
* **Input:** Claim for bariatric consultation (Morbid Obesity exclusion).
* **Expected Decision:** REJECTED (Reason: EXCLUDED_CONDITION)
* **Actual Decision:** `REJECTED` with reason `EXCLUDED_CONDITION`.
* **Match:** ✅ Yes
* **Explanation:** Diagnosis keyword string matches the exclusion policies strictly without necessitating subjective LLM decisions.
