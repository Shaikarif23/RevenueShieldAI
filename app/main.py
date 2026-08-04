from fastapi import FastAPI

app = FastAPI(
    title="RevenueShield AI",
    version="1.0.0",
    description="Restaurant Revenue Leakage Prevention Platform"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to RevenueShield AI",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "server": "Healthy"
    }