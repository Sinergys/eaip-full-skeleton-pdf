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
    meterId: str | None = None


@app.post("/analytics/forecast")
def forecast(req: ForecastReq):
    if not req.series:
        raise HTTPException(status_code=400, detail="series required")
    if req.horizon <= 0:
        raise HTTPException(status_code=400, detail="horizon must be positive")

    try:
        last = req.series[-1].value
        forecast_values = [last for _ in range(req.horizon)]
        return {
            "forecast": forecast_values,
            "meterId": req.meterId,
            "horizon": req.horizon,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Forecast generation failed: {str(e)}"
        )
