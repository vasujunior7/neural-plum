# Test Cases Evaluation Report

**Total Tests:** 17 | **Passed:** 17 | **Failed:** 0

🎉 **All tests passed!** The pipeline conforms exactly to expected behaviors.

> *Note: TC011 purposefully simulates an error in the system to verify graceful degradation, so an `ERROR:root:Fraud component failed` trace in the python execution logs is expected.*

---

## ✅ PASS | TC001: Wrong Document Uploaded
**Description:** Member submits two prescriptions for a consultation claim that requires a prescription and a hospital bill.

### Expected
- **Decision:** None

### Actual Result
- **Final State:** VERIFYING
- **Decision:** None
- **Rejection Reasons:** MISSING_DOCUMENTS
- **Confidence Score:** 100.0%

**Processing Notes:**
- Missing required documents: HOSPITAL_BILL. Uploaded: PRESCRIPTION, PRESCRIPTION

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['Missing required documents: HOSPITAL_BILL. Uploaded: PRESCRIPTION, PRESCRIPTION']

---

## ✅ PASS | TC002: Unreadable Document
**Description:** Member uploads a valid prescription but a blurry, unreadable photo of their pharmacy bill.

### Expected
- **Decision:** None

### Actual Result
- **Final State:** VERIFYING
- **Decision:** None
- **Rejection Reasons:** UNREADABLE_DOCUMENT
- **Confidence Score:** 100.0%

**Processing Notes:**
- Document blurry_bill.jpg is unreadable. Please re-upload.

**Execution Traces:**
- `PLANNING`: ['Claim classified as PHARMACY — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: Low-risk pharmacy claims processed under prescription rules', 'Skipping SemanticFraud: Low-risk pharmacy claims processed under prescription rules']
- `VERIFYING`: ['Document blurry_bill.jpg is unreadable. Please re-upload.']

---

## ✅ PASS | TC003: Documents Belong to Different Patients
**Description:** The prescription is for Rajesh Kumar but the hospital bill is for a different patient, Arjun Mehta.

### Expected
- **Decision:** None

### Actual Result
- **Final State:** VERIFYING
- **Decision:** None
- **Rejection Reasons:** PATIENT_NAME_MISMATCH
- **Confidence Score:** 100.0%

**Processing Notes:**
- Patient names mismatch across documents: found Arjun Mehta and Rajesh Kumar.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['Patient names mismatch across documents: found Arjun Mehta and Rajesh Kumar.']

---

## ✅ PASS | TC004: Clean Consultation — Full Approval
**Description:** Complete, valid consultation claim with correct documents, valid member, covered treatment, within all limits.

### Expected
- **Decision:** APPROVED
- **Approved Amount:** ₹1350

### Actual Result
- **Final State:** DONE
- **Decision:** APPROVED
- **Approved Amount:** ₹1350.0
- **Confidence Score:** 100.0%

**Processing Notes:**
- Co-pay (10.0%) applied on ₹1500.0 = ₹150.0 deducted. Final: ₹1350.0.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ['Co-pay (10.0%) applied on ₹1500.0 = ₹150.0 deducted. Final: ₹1350.0.']
- `SUMMARIZING`: ['✅ Your Consultation claim for ₹1,500 submitted on 2024-11-01 has been approved.\n\n💰 Approved amount: ₹1,350\n\n📋 Adjustments applied:\n  • A 10.0% co-pay was applied to your claim. This means ₹150.0 is your share, and the insurer pays ₹1350.0.\n\nExpected payout within 3–5 business days to your registered bank account.']

---

## ✅ PASS | TC005: Waiting Period — Diabetes
**Description:** Member joined 2024-09-01. Claims for diabetes treatment on 2024-10-15, which is within the 90-day waiting period for diabetes.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** WAITING_PERIOD

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** WAITING_PERIOD
- **Confidence Score:** 90.0%

**Processing Notes:**
- Condition 'diabetes' has a waiting period of 90 days. Eligible from 2024-11-30.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ["Condition 'diabetes' has a waiting period of 90 days. Eligible from 2024-11-30."]
- `SUMMARIZING`: ['❌ Your Consultation claim for ₹3,000 submitted on 2024-10-15 has been rejected.\n\n📋 Reason(s):\n  • Your policy requires 90 days of active coverage before diabetes-related claims are eligible. Your coverage started on 2024-09-01, and this claim was filed only 44 days later on 2024-10-15. You will be eligible from 2024-11-30.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly.']

---

## ✅ PASS | TC006: Dental Partial Approval — Cosmetic Exclusion
**Description:** Bill includes root canal treatment (covered) and teeth whitening (cosmetic, excluded). System must approve only the covered procedure.

### Expected
- **Decision:** PARTIAL
- **Approved Amount:** ₹8000

### Actual Result
- **Final State:** DONE
- **Decision:** PARTIAL
- **Approved Amount:** ₹8000.0
- **Confidence Score:** 90.0%

**Processing Notes:**

**Execution Traces:**
- `PLANNING`: ['Claim classified as DENTAL — Fast Track', 'Complexity score: 0.50', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: Dental claims processed under separate sub-limit rules', 'Skipping SemanticFraud: Dental claims processed under separate sub-limit rules']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: Dental claims processed under separate sub-limit rules']
- `SEMANTIC_FRAUD`: ['Skipped: Dental claims processed under separate sub-limit rules']
- `DECIDING`: []
- `SUMMARIZING`: ["⚠️ Your Dental claim for ₹12,000 submitted on 2024-10-15 has been partially approved.\n\n💰 Approved amount: ₹8,000\n\n❌ Not covered:\n  • The procedure 'Teeth Whitening' costing ₹4000.0 is classified as a cosmetic/excluded dental procedure ('Teeth Whitening') and is not covered under your policy.\n\nExpected payout within 3–5 business days to your registered bank account."]

---

## ✅ PASS | TC007: MRI Without Pre-Authorization
**Description:** MRI scan costing ₹15,000 submitted without pre-authorization. Policy requires pre-auth for MRI above ₹10,000.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** PRE_AUTH_MISSING

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** PRE_AUTH_MISSING
- **Confidence Score:** 100.0%

**Processing Notes:**
- MRI requires pre-authorization when amount > 10000.0
- Please obtain pre-authorization and resubmit.

**Execution Traces:**
- `PLANNING`: ['Claim classified as DIAGNOSTIC — Full Pipeline', 'Complexity score: 0.70', 'Agents to run: DocVerification, Extraction, FraudCheck, Decision', 'Skipping SemanticFraud: Standard diagnostic claims use rule-based fraud checks only']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `SEMANTIC_FRAUD`: ['Skipped: Standard diagnostic claims use rule-based fraud checks only']
- `DECIDING`: ['MRI requires pre-authorization when amount > 10000.0', 'Please obtain pre-authorization and resubmit.']
- `SUMMARIZING`: ['❌ Your Diagnostic claim for ₹15,000 submitted on 2024-11-02 has been rejected.\n\n📋 Reason(s):\n  • Your MRI Lumbar Spine costing ₹15000.0 requires pre-authorization because it exceeds the ₹10000.0 threshold. Please obtain pre-authorization from your insurer and resubmit.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly.']

---

## ✅ PASS | TC008: Per-Claim Limit Exceeded
**Description:** Claimed amount of ₹7,500 exceeds the per-claim limit of ₹5,000.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** PER_CLAIM_EXCEEDED

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** PER_CLAIM_EXCEEDED
- **Confidence Score:** 100.0%

**Processing Notes:**
- Claimed amount ₹7500.0 exceeds the per-claim limit of ₹5000.0

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ['Claimed amount ₹7500.0 exceeds the per-claim limit of ₹5000.0']
- `SUMMARIZING`: ['❌ Your Consultation claim for ₹7,500 submitted on 2024-10-20 has been rejected.\n\n📋 Reason(s):\n  • Your claimed amount of ₹7500.0 exceeds the per-claim limit of ₹5000.0 for consultation claims. Please split the claim or contact your HR for higher limit options.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly.']

---

## ✅ PASS | TC009: Fraud Signal — Multiple Same-Day Claims
**Description:** Member EMP008 has already submitted 3 claims today before this one arrives. This is the 4th claim from the same member on the same day.

### Expected
- **Decision:** MANUAL_REVIEW

### Actual Result
- **Final State:** FRAUD_CHECKING
- **Decision:** MANUAL_REVIEW
- **Rejection Reasons:** MANUAL_REVIEW
- **Confidence Score:** 72.0%

**Processing Notes:**
- Member has 3 previous claims on the same day. Limit is 2.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.70', 'Agents to run: DocVerification, Extraction, FraudCheck, Decision', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Member has 3 previous claims on the same day. Limit is 2.']

---

## ✅ PASS | TC010: Network Hospital — Discount Applied
**Description:** Valid claim at Apollo Hospitals, a network hospital. Network discount must be applied before co-pay.

### Expected
- **Decision:** APPROVED
- **Approved Amount:** ₹3240

### Actual Result
- **Final State:** DONE
- **Decision:** APPROVED
- **Approved Amount:** ₹3240.0
- **Confidence Score:** 100.0%

**Processing Notes:**
- Network discount (20.0%) applied first on ₹4500.0 = ₹3600.0.
- Co-pay (10.0%) applied on ₹3600.0 = ₹360.0 deducted. Final: ₹3240.0.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ['Network discount (20.0%) applied first on ₹4500.0 = ₹3600.0.', 'Co-pay (10.0%) applied on ₹3600.0 = ₹360.0 deducted. Final: ₹3240.0.']
- `SUMMARIZING`: ["✅ Your Consultation claim for ₹4,500 submitted on 2024-11-03 has been approved.\n\n💰 Approved amount: ₹3,240\n\n📋 Adjustments applied:\n  • A 20.0% network hospital discount was applied because 'Apollo Hospitals' is in the insurer's network. This reduced the billable amount from ₹4500.0 to ₹3600.0.\n  • A 10.0% co-pay was applied to your claim. This means ₹360.0 is your share, and the insurer pays ₹3240.0.\n\nExpected payout within 3–5 business days to your registered bank account."]

---

## ✅ PASS | TC011: Component Failure — Graceful Degradation
**Description:** One component of your system fails mid-processing (simulate with the flag below). The overall pipeline must continue, produce a decision, and make the failure visible in the output with an appropriately reduced confidence score.

### Expected
- **Decision:** APPROVED

### Actual Result
- **Final State:** DONE
- **Decision:** APPROVED
- **Approved Amount:** ₹4000.0
- **Confidence Score:** 80.0%

**Processing Notes:**

**Execution Traces:**
- `PLANNING`: ['Claim classified as ALTERNATIVE_MEDICINE — Full Pipeline', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, FraudCheck, Decision', 'Skipping SemanticFraud: Alternative medicine uses practitioner validation instead']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Fraud checking bypassed due to failure: Simulated Fraud API timeout']
- `SEMANTIC_FRAUD`: ['Skipped: Alternative medicine uses practitioner validation instead']
- `DECIDING`: []
- `SUMMARIZING`: ['✅ Your Alternative Medicine claim for ₹4,000 submitted on 2024-10-28 has been approved.\n\n💰 Approved amount: ₹4,000\n\nExpected payout within 3–5 business days to your registered bank account.']

---

## ✅ PASS | TC012: Excluded Treatment
**Description:** Member claims for bariatric consultation and a diet program. Obesity treatment is explicitly excluded under the policy.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** EXCLUDED_CONDITION

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** EXCLUDED_CONDITION
- **Confidence Score:** 100.0%

**Processing Notes:**
- Diagnosis 'Morbid Obesity — BMI 37' matches exclusion policy: 'Obesity and weight loss programs'

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ["Diagnosis 'Morbid Obesity — BMI 37' matches exclusion policy: 'Obesity and weight loss programs'"]
- `SUMMARIZING`: ["❌ Your Consultation claim for ₹8,000 submitted on 2024-10-18 has been rejected.\n\n📋 Reason(s):\n  • Your diagnosis 'Morbid Obesity — BMI 37' matches the excluded category 'Obesity and weight loss programs'. This type of treatment is not covered under your current policy.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly."]

---

## ✅ PASS | TC013: Dependent Claim — Family Floater
**Description:** Claim submitted for a dependent (spouse) of the primary member. Should map to the family floater limit.

### Expected
- **Decision:** APPROVED
- **Approved Amount:** ₹900

### Actual Result
- **Final State:** DONE
- **Decision:** APPROVED
- **Approved Amount:** ₹900.0
- **Confidence Score:** 100.0%

**Processing Notes:**
- Co-pay (10.0%) applied on ₹1000.0 = ₹100.0 deducted. Final: ₹900.0.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ['Co-pay (10.0%) applied on ₹1000.0 = ₹100.0 deducted. Final: ₹900.0.']
- `SUMMARIZING`: ['✅ Your Consultation claim for ₹1,000 submitted on 2024-11-10 has been approved.\n\n💰 Approved amount: ₹900\n\n📋 Adjustments applied:\n  • A 10.0% co-pay was applied to your claim. This means ₹100.0 is your share, and the insurer pays ₹900.0.\n\nExpected payout within 3–5 business days to your registered bank account.']

---

## ✅ PASS | TC014: Pharmacy — Branded Drug Copay
**Description:** Member submits a pharmacy claim for branded drugs. Policy requires a 30% copay for branded drugs.

### Expected
- **Decision:** APPROVED
- **Approved Amount:** ₹1400

### Actual Result
- **Final State:** DONE
- **Decision:** APPROVED
- **Approved Amount:** ₹1400.0
- **Confidence Score:** 100.0%

**Processing Notes:**
- Co-pay (30.0%) applied on ₹2000.0 = ₹600.0 deducted. Final: ₹1400.0.

**Execution Traces:**
- `PLANNING`: ['Claim classified as PHARMACY — Fast Track', 'Complexity score: 0.20', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: Low-risk pharmacy claims processed under prescription rules', 'Skipping SemanticFraud: Low-risk pharmacy claims processed under prescription rules']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: Low-risk pharmacy claims processed under prescription rules']
- `SEMANTIC_FRAUD`: ['Skipped: Low-risk pharmacy claims processed under prescription rules']
- `DECIDING`: ['Co-pay (30.0%) applied on ₹2000.0 = ₹600.0 deducted. Final: ₹1400.0.']
- `SUMMARIZING`: ['✅ Your Pharmacy claim for ₹2,000 submitted on 2024-11-05 has been approved.\n\n💰 Approved amount: ₹1,400\n\n📋 Adjustments applied:\n  • A 30.0% co-pay was applied to your claim. This means ₹600.0 is your share, and the insurer pays ₹1400.0.\n\nExpected payout within 3–5 business days to your registered bank account.']

---

## ✅ PASS | TC015: Vision — Mixed Coverage (LASIK + Eye Exam)
**Description:** Bill includes an eye examination (covered) and LASIK surgery (excluded).

### Expected
- **Decision:** PARTIAL
- **Approved Amount:** ₹2000

### Actual Result
- **Final State:** DONE
- **Decision:** PARTIAL
- **Approved Amount:** ₹2000.0
- **Confidence Score:** 100.0%

**Processing Notes:**

**Execution Traces:**
- `PLANNING`: ['Claim classified as VISION — Full Pipeline', 'Complexity score: 0.90', 'Agents to run: DocVerification, Extraction, FraudCheck, SemanticFraud, Decision']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `SEMANTIC_FRAUD`: ['Semantic fraud score: 0.00 — Low risk', 'No significant anomalies detected.']
- `DECIDING`: []
- `SUMMARIZING`: ["⚠️ Your Vision claim for ₹42,000 submitted on 2024-11-12 has been partially approved.\n\n💰 Approved amount: ₹2,000\n\n❌ Not covered:\n  • The item 'LASIK Surgery' costing ₹40000.0 is classified as an excluded vision item ('LASIK Surgery') and is not covered under your policy.\n\nExpected payout within 3–5 business days to your registered bank account."]

---

## ✅ PASS | TC016: Maternity During Waiting Period
**Description:** Maternity claim submitted within the 270-day waiting period.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** WAITING_PERIOD

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** WAITING_PERIOD
- **Confidence Score:** 90.0%

**Processing Notes:**
- Condition 'maternity' has a waiting period of 270 days. Eligible from 2024-12-27.

**Execution Traces:**
- `PLANNING`: ['Claim classified as CONSULTATION — Fast Track', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, Decision', 'Skipping FraudCheck: OPD consultation claims are low-risk; skip rule-based fraud for speed', 'Skipping SemanticFraud: OPD consultation claims below high-value threshold are low-risk']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Skipped: OPD consultation claims are low-risk; skip rule-based fraud for speed']
- `SEMANTIC_FRAUD`: ['Skipped: OPD consultation claims below high-value threshold are low-risk']
- `DECIDING`: ["Condition 'maternity' has a waiting period of 270 days. Eligible from 2024-12-27."]
- `SUMMARIZING`: ['❌ Your Consultation claim for ₹2,000 submitted on 2024-08-10 has been rejected.\n\n📋 Reason(s):\n  • Your policy requires 270 days of active coverage before maternity-related claims are eligible. Your coverage started on 2024-04-01, and this claim was filed only 131 days later on 2024-08-10. You will be eligible from 2024-12-27.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly.']

---

## ✅ PASS | TC017: Alternative Medicine — Limit Exceeded
**Description:** Claim for alternative medicine where the member has exceeded the maximum 20 sessions per year limit.

### Expected
- **Decision:** REJECTED
- **Rejection Reasons:** SESSION_LIMIT_EXCEEDED

### Actual Result
- **Final State:** DONE
- **Decision:** REJECTED
- **Rejection Reasons:** SESSION_LIMIT_EXCEEDED
- **Confidence Score:** 100.0%

**Processing Notes:**
- Member has used 21 sessions. Max limit is 20 per year.

**Execution Traces:**
- `PLANNING`: ['Claim classified as ALTERNATIVE_MEDICINE — Full Pipeline', 'Complexity score: 0.40', 'Agents to run: DocVerification, Extraction, FraudCheck, Decision', 'Skipping SemanticFraud: Alternative medicine uses practitioner validation instead']
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `SEMANTIC_FRAUD`: ['Skipped: Alternative medicine uses practitioner validation instead']
- `DECIDING`: ['Member has used 21 sessions. Max limit is 20 per year.']
- `SUMMARIZING`: ['❌ Your Alternative Medicine claim for ₹1,500 submitted on 2024-11-20 has been rejected.\n\n📋 Reason(s):\n  • You have already reached the maximum allowed limit of 20 alternative medicine sessions for this policy year.\n\nIf you believe this is incorrect, please contact your HR or the insurer directly.']

---

