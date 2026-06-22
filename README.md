---
title: Neural Plum App
emoji: 🏢
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# 🌟 Neural Plum

<div align="center">
  <img src="frontend/src/assets/hero.png" width="200" alt="Neural Plum Logo" />
  <h3>An advanced, AI-powered Multi-Agent System for Health Insurance Claims Processing</h3>
  <p>Automate end-to-end adjudication with Explainability, Semantic Fraud Detection, and Graceful Degradation.</p>
</div>

---

Neural Plum completely revolutionizes how health insurance claims are processed. By leveraging an orchestration of specialized AI agents, it seamlessly handles everything from document verification to deep semantic fraud analysis, instantly applying complex policy rules (like copays, waiting periods, and exclusions) with full transparency and explainability.

## ✨ Key Features & Upgrades

Neural Plum isn't just an LLM wrapper—it's a robust multi-agent orchestration pipeline.

- **🤖 Multi-Agent Pipeline & Planner:** Dynamic execution! A new **Planner Agent** orchestrates Specialized agents (Verification, Extraction, Fraud, Decision) based on claim complexity, optimizing speed and cost.
- **🧠 Semantic Fraud Detection:** Beyond rigid rules, the AI performs semantic analysis on diagnoses and line items to flag suspicious behavior (e.g., mismatched treatment contexts or drug-seeking behavior).
- **📊 Explainability Layer:** No black boxes! The system generates a detailed **Policy Rationale Breakdown** for every decision, citing exact policy clauses and mathematical thresholds.
- **💬 Automated Case Summaries:** Instantly generates empathetic, user-friendly markdown summaries explaining the exact financial breakdown and rejection/approval logic to the claimant.
- **🛡️ Graceful Degradation:** The pipeline never fully crashes. If a non-critical component (like the Fraud Agent) fails, the system continues processing and adjusts the output **Confidence Score** accordingly.
- **✅ Handler Checklist:** For claims routed to `MANUAL_REVIEW`, a dedicated agent generates an actionable checklist for human handlers, highlighting exactly what triggered the review.

## 🛠️ Tech Stack

> [!NOTE]
> Neural Plum is built to be modern, scalable, and reactive.

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 19, Vite, Tailwind CSS v4, Framer Motion, Recharts
- **AI / LLM**: Google GenAI (Gemini)
- **Observability**: Langfuse (Tracing & Monitoring)
- **Database**: SQLite (`plum_claims.db`)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/user/neural-plum.git
cd neural-plum
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

> [!IMPORTANT]  
> Configure the following variables in `backend/.env`:

| Variable | Description | Example |
| -------- | ----------- | ------- |
| `GEMINI_API_KEY` | Your Google Gemini API Key | `AIza...` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse Public Key | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | Langfuse Secret Key | `sk-lf-...` |
| `LANGFUSE_HOST` | Langfuse Host | `https://cloud.langfuse.com` |
| `MOCK_EXTRACTION` | True/False for Mock Mode | `False` |

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Start Development Servers

You will need two terminal windows.

```bash
# Terminal 1: Backend FastAPI Server
cd backend
# Activate virtual env on Windows: venv\Scripts\activate
# Activate virtual env on Linux/Mac: source venv/bin/activate
uvicorn src.main:app --reload
```

```bash
# Terminal 2: Frontend Vite Server
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🏗️ Architecture & Request Lifecycle

1. **Submission:** Claim submitted with documents and member details.
2. **Planning:** `PlannerAgent` assesses complexity (Fast Track vs. Comprehensive) and decides which agents to invoke.
3. **Verification:** `DocumentVerificationAgent` ensures required documents exist and are readable.
4. **Extraction:** `ExtractionAgent` pulls structured data using Gemini, calculating per-field confidence scores.
5. **Fraud Analysis:** `FraudCheckingAgent` checks frequency limits, while `SemanticFraudAgent` assesses behavioral risk.
6. **Decision:** `DecisionAgent` applies copays, waiting periods, network discounts, and exclusions.
7. **Synthesis:** `CaseSummaryAgent` and `HandlerChecklistAgent` generate beautiful, actionable text for claimants and adjusters.

## 🧪 Testing & Ground Truth Evaluation

The pipeline has been rigorously evaluated against 12 complex, deterministic ground-truth scenarios. 

To run the evaluation suite and generate the Markdown report:

```bash
cd backend
python generate_report.py
```

### 🏆 Test Results

> [!TIP]  
> **Total Tests:** 12 | **Passed:** 12 | **Failed:** 0  
> *All 12 scenarios successfully match the 100% deterministic ground-truth JSON definitions.*

We covered the following scenarios:
1. **Wrong Document Uploaded**: Safely halted execution at VERIFYING stage.
2. **Unreadable Document**: Detected blurry document and requested re-upload.
3. **Documents Belong to Different Patients**: Detected cross-patient mismatch securely.
4. **Clean Consultation**: Fully approved with a 10% copay applied successfully.
5. **Waiting Period — Diabetes**: Automatically rejected due to a strict 90-day waiting period policy.
6. **Dental Partial Approval**: Extracted multiple line items and partially approved by excluding the cosmetic procedure.
7. **MRI Without Pre-Authorization**: Rejected strictly according to the limit bounds logic (above ₹10,000 without pre-auth).
8. **Per-Claim Limit Exceeded**: Rejected dynamically enforcing policy limit caps.
9. **Fraud Signal — Multiple Same-Day Claims**: Flagged for `MANUAL_REVIEW` due to frequency rules.
10. **Network Hospital**: Applied 20% network discount before the standard copay smoothly.
11. **Component Failure**: Handled a simulated fraud-agent timeout with Graceful Degradation, yielding `APPROVED` with a reduced confidence score.
12. **Excluded Treatment**: Rejected bariatric treatment by strictly matching condition exclusion keywords.

## 💡 Troubleshooting

> [!WARNING]  
> **LLM Extraction Returning Empty?**
> If you are hitting `503 Service Unavailable` errors with the Gemini API, set `MOCK_EXTRACTION=True` in your `.env`. The system will gracefully fall back to a dynamic mock generator that still allows you to test the full pipeline on the frontend!

---
<div align="center">
  <i>Built with ❤️ for the future of automated healthcare.</i>
</div>
