# RevenueShield AI

RevenueShield AI is a full-stack revenue intelligence platform for detecting revenue leakage in food-delivery operations.

## What the MVP does

- JWT authentication and ADMIN role protection
- Order, restaurant and payment management
- Expected vs collected revenue analysis
- Delivered-order revenue leakage detection
- Data-quality anomaly detection
- Risk scoring (HIGH / MEDIUM / LOW)
- Restaurant-level leakage analysis
- Top leaked orders
- Alerts and actionable recommendations (included in dashboard overview)
- React admin dashboard with restaurant/date/risk filters

## Architecture

React + Vite → FastAPI → SQLAlchemy → PostgreSQL

## Project structure

```text
RevenueShieldAI/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    ├── package.json
    └── .env.example
```

## Run the backend

From `RevenueShieldAI/backend`:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your PostgreSQL connection and secret.

Then:

```bash
alembic upgrade head
python -m uvicorn main:app --reload --port 8000
```

Swagger:
`http://127.0.0.1:8000/docs`

## Run the frontend

From `RevenueShieldAI/frontend`:

```bash
npm install
npm run dev
```

Open:
`http://localhost:5173`

The Vite development server proxies `/api/*` to FastAPI. The frontend therefore calls `/api/dashboard/...` while FastAPI receives `/dashboard/...`.

For a deployed backend, create `frontend/.env` from `.env.example` and set:

```text
VITE_API_BASE_URL=https://your-backend.example.com
```

## Verified business scenario

The current test data demonstrates:

- Order #8
- Restaurant: Paradise Biryani
- Expected revenue: ₹580
- Successful payment collected: ₹0
- Leakage: ₹580
- Risk score: 85
- Risk level: HIGH
- Recommendation: investigate payment settlement

## Next product phase

The MVP is complete. The next phase can add ML-based leakage probability, payment/POS integrations, case management, recovery tracking and cloud deployment.
