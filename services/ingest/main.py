from fastapi import FastAPI, UploadFile, File, HTTPException
from uuid import uuid4
import os
import httpx

app = FastAPI(title="EAIP ingest", version="0.1.0")

@app.get("/health")
def health():
    return {"service": "ingest", "status": "ok"}

@app.post("/ingest/files")
async def ingest_files(file: UploadFile = File(...)):
    batch_id = str(uuid4())
    save_path = f"/tmp/ingest_{batch_id}_{file.filename}"

    # Save uploaded file
    try:
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Call validate service
    validate_resp = {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://validate:8002/validate/run",
                json={"batchId": batch_id},
            )
            validate_resp = resp.json()
    except Exception as e:
        validate_resp = {"error": f"validate call failed: {e}"}

    return {"batchId": batch_id, "filename": file.filename, "validate": validate_resp}
