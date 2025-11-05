from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="EAIP recommend", version="0.1.0")

@app.get("/health")
def health():
    return {"service":"recommend","status":"ok"}

class Measure(BaseModel):
    code: str
    title: str
    capex_usd: float
    annual_saving_usd: float
    payback_years: float
    priority: int

class Req(BaseModel):
    auditId: str

@app.post("/recommend/generate")
def generate(req: Req) -> dict:
    measures: List[Measure] = [
        Measure(code="LED-01", title="Замена на LED", capex_usd=5000, annual_saving_usd=2500, payback_years=2.0, priority=1),
        Measure(code="VFD-02", title="Частотники насосов", capex_usd=12000, annual_saving_usd=4800, payback_years=2.5, priority=2),
        Measure(code="INS-03", title="Теплоизоляция", capex_usd=3000, annual_saving_usd=900, payback_years=3.3, priority=3),
    ]
    return {"auditId": req.auditId, "measures": [m.model_dump() for m in measures]}
