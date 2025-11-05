from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="EAIP validate", version="0.1.0")

class ValidateReq(BaseModel):
    batchId: str

@app.get("/health")
def health():
    return {"service": "validate", "status": "ok"}

@app.post("/validate/run")
def validate_run(req: ValidateReq):
    # Заглушка: всегда «passed»
    return {"batchId": req.batchId, "passed": True, "issues": []}
