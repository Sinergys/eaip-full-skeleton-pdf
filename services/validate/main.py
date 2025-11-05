from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="EAIP validate", version="0.1.0")

class ValidateReq(BaseModel):
    batchId: str

@app.get("/health")
def health():
    return {"service": "validate", "status": "ok"}

@app.post("/validate/run")
def validate_run(req: ValidateReq):
    try:
        if not req.batchId or not req.batchId.strip():
            raise HTTPException(status_code=400, detail="batchId is required and cannot be empty")
        
        # Заглушка: всегда «passed»
        # В реальной реализации здесь будет проверка данных
        return {
            "batchId": req.batchId,
            "passed": True,
            "issues": []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
