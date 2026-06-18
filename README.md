# Neural Plum

An AI-powered multi-agent pipeline for automated health insurance claims processing. Neural Plum handles end-to-end claim adjudication, including document verification, structured data extraction, fraud detection, and policy application (copays, waiting periods, network discounts, and exclusions) with graceful degradation.

## Key Features

- **Multi-Agent Pipeline**: Specialized agents for Document Verification, Information Extraction, Fraud Checking, and Decision Making.
- **Robust Policy Engine**: Automatically enforces copays, waiting periods, per-claim limits, and network discounts based on policy configurations.
- **Fraud Detection**: Identifies suspicious patterns like multiple same-day claims and escalates to manual review to avoid false-positive rejections.
- **Graceful Degradation**: Continues processing and adjusting confidence scores even if a non-critical component (like the Fraud Agent) fails mid-execution.
- **Comprehensive Observability**: Tracing and monitoring powered by Langfuse.

## Tech Stack

- **Backend**: Python 3.x, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 19, Vite, Tailwind CSS, Framer Motion, Recharts
- **AI / LLM**: Google GenAI
- **Observability**: Langfuse
- **Database**: SQLite (plum_claims.db)

## Prerequisites

- Python 3.10 or higher
- Node.js 20 or higher
- npm or pnpm
- Google Gemini API Key (for LLM extraction)
- Langfuse API Keys (for tracing)

## Getting Started

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

Configure the following variables in `backend/.env`:

| Variable | Description | Example |
| -------- | ----------- | ------- |
| `GEMINI_API_KEY` | Your Google Gemini API Key | `AIza...` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse Public Key | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | Langfuse Secret Key | `sk-lf-...` |
| `LANGFUSE_HOST` | Langfuse Host | `https://cloud.langfuse.com` |

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

## Architecture

### Directory Structure

```
├── backend/
│   ├── src/
│   │   ├── agents/          # Multi-agent system (base, supervisor)
│   │   ├── llm/             # Google GenAI integration
│   │   ├── policy/          # Policy Engine rules and configuration
│   │   ├── routes/          # FastAPI API endpoints
│   │   ├── tracing/         # Langfuse observability setup
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── models.py        # Pydantic schemas (ClaimSubmission, etc.)
│   │   ├── db_models.py     # SQLAlchemy models
│   │   └── database.py      # Database connection setup
│   ├── tests/               # Backend tests
│   ├── run_tests.py         # Test execution script
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/                 # React source code
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.ts       # Vite configuration
├── policy_terms.json        # Policy configuration, limits, roster
└── test_cases.json          # Deterministic scenarios for testing
```

### Request Lifecycle

1. A claim is submitted containing documents and member details.
2. `Supervisor` triggers the `DocumentVerificationAgent` to ensure all required documents exist and are readable.
3. If verified, the `ExtractionAgent` processes document contents (using Google GenAI or mock fallback) to extract structured data.
4. `FraudCheckingAgent` evaluates the structured data against fraud rules (e.g. multiple claims in a single day).
5. Finally, the `DecisionAgent` (PolicyEngine) applies copays, checks waiting periods, network discounts, and specific exclusions.
6. A final decision (`APPROVED`, `REJECTED`, `PARTIAL`, `MANUAL_REVIEW`, `NEEDS_REUPLOAD`) is returned along with confidence scores and logs.

## Environment Variables

### Required (Backend `.env`)

| Variable | Description |
| -------- | ----------- |
| `GEMINI_API_KEY` | Google Gemini API Key for LLM extraction |
| `LANGFUSE_SECRET_KEY` | Secret Key for Langfuse tracing |
| `LANGFUSE_PUBLIC_KEY` | Public Key for Langfuse tracing |
| `LANGFUSE_HOST` | Host URL for Langfuse |

## Available Scripts

### Backend (`/backend`)

| Command | Description |
| ------- | ----------- |
| `uvicorn src.main:app --reload` | Start the FastAPI development server |
| `python run_tests.py` | Run the complete 12 deterministic test scenarios and generate `test_results.md` |

### Frontend (`/frontend`)

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start the Vite development server |
| `npm run build` | Build the frontend for production |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint to find issues |

## Testing & Evaluation Results

The pipeline has been thoroughly evaluated against 12 complex deterministic scenarios covering different edge cases in health insurance adjudication.

### Test Execution

To run the evaluation suite:

```bash
cd backend
python run_tests.py
```

This processes the claims in `test_cases.json` and outputs a comprehensive `test_results.md` report.

### Test Results

**Total Tests:** 12 | **Passed:** 12 | **Failed:** 0

🎉 **All tests passed!** The pipeline conforms exactly to expected behaviors.

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
11. **Component Failure**: Handled a simulated fraud-agent timeout with Graceful Degradation, yielding `APPROVED` with reduced confidence score.
12. **Excluded Treatment**: Rejected bariatric treatment by strictly matching condition exclusion keywords.

## Deployment

### Docker (Recommended)

1. Ensure you have a `Dockerfile` for both backend and frontend.
2. Create a `docker-compose.yml` that configures the FastAPI and React containers along with environment variable mapping.
3. Run `docker-compose up -d --build` to run Neural Plum seamlessly.

### Manual / VPS

**Backend**: Deploy FastAPI on a VPS using `gunicorn` with Uvicorn workers.
**Frontend**: Build the static files using `npm run build` and serve them via Nginx or a static hosting provider like Vercel or Netlify.

## Troubleshooting

### LLM Extraction Fails

**Error:** Unstructured responses or API limits reached.
**Solution:** Check `GEMINI_API_KEY`. If developing locally without a key, ensure `settings.MOCK_EXTRACTION = True` is utilized to leverage the fallback mock structured extraction mechanisms during tests.

### Missing Langfuse Metrics

**Error:** Tracing logs aren't appearing on Langfuse dashboard.
**Solution:** Verify all three `LANGFUSE_*` environment variables in your backend `.env` file are exactly matching your project settings.

### Database Errors

**Error:** `sqlalchemy.exc.OperationalError: no such table`
**Solution:** Ensure SQLite is correctly initialized. Re-running the main server or running initialization scripts typically triggers SQLAlchemy to create all missing tables automatically.
