from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="EAIP analytics", version="0.1.0")

@app.get("/health")
def health():
    return {"service": "analytics", "status": "ok"}

class Point(BaseModel):
    ts: str
    value: float

class ForecastReq(BaseModel):
    series: List[Point]
    horizon: int

@app.post("/analytics/forecast")
def forecast(req: ForecastReq):
    if not req.series:
        raise HTTPException(400, "series required")
    last = req.series[-1].value
    return {"forecast": [last for _ in range(req.horizon)]}
