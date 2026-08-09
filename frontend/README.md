# RevenueShield AI Frontend

React + Vite frontend for the completed RevenueShield AI FastAPI backend.

## Backend endpoints used

Authentication:
- POST /auth/login
- GET /me

Dashboard:
- GET /dashboard/overview
- GET /dashboard/revenue
- GET /dashboard/restaurant-leakage
- GET /dashboard/anomalies
- GET /dashboard/alerts

Restaurants:
- GET /restaurants/
- GET /restaurants/{restaurant_id}

## Run

1. Start the FastAPI backend on port 8000.
2. Open this frontend folder.
3. Run `npm install`.
4. Run `npm run dev`.
5. Open http://localhost:5173.

The Vite development server proxies `/api/*` to `http://127.0.0.1:8000/*`.

The dashboard is ADMIN-only because the backend dashboard routes require ADMIN.
