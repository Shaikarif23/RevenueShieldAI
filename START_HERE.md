# RevenueShield AI — Start Here

## 1. Backend

Open Command Prompt in:

```text
F:\RevenueShieldAI\backend
```

Create/activate the virtual environment:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy:

```text
backend\.env.example
```

to:

```text
backend\.env
```

Set your PostgreSQL password/database values.

Run migrations:

```bat
alembic upgrade head
```

Start FastAPI:

```bat
python -m uvicorn main:app --reload --port 8000
```

Check:

```text
http://127.0.0.1:8000/docs
```

## 2. Frontend

Open a second Command Prompt in:

```text
F:\RevenueShieldAI\frontend
```

Run:

```bat
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## 3. Login

Use an existing ADMIN account from your database.

The frontend sends:

```text
POST /api/auth/login
```

Vite proxies that request to:

```text
POST http://127.0.0.1:8000/auth/login
```

## 4. Dashboard

The dashboard calls:

```text
GET /dashboard/overview
```

The overview now contains:

- summary
- risk_summary
- top_leaked_orders
- restaurant_leakage
- recent_anomalies
- alerts

The dedicated alert page still uses:

```text
GET /dashboard/alerts
```

## 5. Important

Do not commit `.env` files, passwords, database credentials or `.git`.

This package intentionally excludes the previous Git metadata and environment secrets.
