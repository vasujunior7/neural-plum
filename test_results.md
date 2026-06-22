# Test Cases Evaluation Report

**Total Tests:** 12 | **Passed:** 12 | **Failed:** 0

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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ['Co-pay (10.0%) applied on ₹1500.0 = ₹150.0 deducted. Final: ₹1350.0.']

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
- **Confidence Score:** 100.0%

**Processing Notes:**
- Condition 'diabetes' has a waiting period of 90 days. Eligible from 2024-11-30.

**Execution Traces:**
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ["Condition 'diabetes' has a waiting period of 90 days. Eligible from 2024-11-30."]

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
- **Confidence Score:** 100.0%

**Processing Notes:**

**Execution Traces:**
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: []

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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ['MRI requires pre-authorization when amount > 10000.0', 'Please obtain pre-authorization and resubmit.']

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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ['Claimed amount ₹7500.0 exceeds the per-claim limit of ₹5000.0']

---

## ✅ PASS | TC009: Fraud Signal — Multiple Same-Day Claims
**Description:** Member EMP008 has already submitted 3 claims today before this one arrives. This is the 4th claim from the same member on the same day.

### Expected
- **Decision:** MANUAL_REVIEW

### Actual Result
- **Final State:** FRAUD_CHECKING
- **Decision:** MANUAL_REVIEW
- **Rejection Reasons:** MANUAL_REVIEW
- **Confidence Score:** 80.0%

**Processing Notes:**
- Member has 3 previous claims on the same day. Limit is 2.

**Execution Traces:**
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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ['Network discount (20.0%) applied first on ₹4500.0 = ₹3600.0.', 'Co-pay (10.0%) applied on ₹3600.0 = ₹360.0 deducted. Final: ₹3240.0.']

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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['Fraud checking bypassed due to failure: Simulated Fraud API timeout']
- `DECIDING`: []

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
- `VERIFYING`: ['All documents verified successfully.']
- `EXTRACTING`: ['Extracted data from mock structured content.']
- `FRAUD_CHECKING`: ['No fraud signals detected.']
- `DECIDING`: ["Diagnosis 'Morbid Obesity — BMI 37' matches exclusion policy: 'Obesity and weight loss programs'"]

---

