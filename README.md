# Sunny Demo - Lead Intelligence Copilot

Web demo for showing Cognitive Labs capability to transform B2B lead lists into:
- ranked and explainable lead priorities
- outreach-ready drafts
- exportable sales outputs

## Stack
- Frontend: React + Vite
- Backend: FastAPI
- AI mode: Optional OpenAI integration via backend key
- Language support: Built-in EN/CN toggle (UI + outreach output)

## Project Structure
- `frontend/` React app
- `backend/` FastAPI API
- `sample-data/` demo CSV + product context
- `docs/` implementation + deployment notes

## Quick Start

### 1) Start backend
```bash
cd backend
cp .env.example .env
./run.sh
```

### 2) Start frontend
```bash
cd frontend
cp .env.example .env
./run.sh
```

Frontend will run on `http://localhost:5173` and call backend on `http://localhost:8000`.

## Optional AI Mode
Set backend `.env`:
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Then enable **Use AI-generated outreach** in the UI.

## Model A/B Test
Use this to compare models on the same lead set before selecting production model:
```bash
cd backend
source .venv/bin/activate
python scripts/model_ab_test.py --models "gpt-4o-mini,gpt-4.1-mini,gpt-4o" --language CN --top-n 6
```
Outputs:
- `backend/abtest_output/model_ab_summary.csv`
- `backend/abtest_output/model_ab_details.csv`
- `backend/abtest_output/model_ab_report.md`

## Sample Demo Flow
1. Click **Load Sample Data**
2. Or click **Download Lead Template** and fill in your own leads
3. Click **Run Lead Intelligence**
4. Inspect ranked leads, reasoning, and outreach drafts
5. Download CSV/report to show output handoff

## Product Rule (Going Forward)
- New user-facing features should support EN/CN toggle by default unless explicitly scoped otherwise.
