# Operator Runbook

## 1. Local Development Setup

### Backend & ML
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install scikit-learn joblib scipy numpy pytest
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 2. Docker Deployment
```bash
# Build and start services
docker-compose up --build -d

# Verify health status
curl http://localhost:8000/api/health
```

---

## 3. Retraining Workflow (Module 3)
To initiate an audited offline model retraining round using consented student feedback:
```bash
python ml/pipeline/retrain.py v1.2.0
```
- If the candidate model matches or exceeds the active model on the frozen human benchmark, it is published automatically as active.
- If it underperforms, the round is logged as `rejected` and the active model remains unchanged.

