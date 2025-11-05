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
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    batch_id = str(uuid4())
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(file.filename)
    save_path = f"/tmp/ingest_{batch_id}_{safe_filename}"

    # Save uploaded file
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file not allowed")
        
        with open(save_path, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=500, detail=f"Permission denied when saving file: {e}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error saving file: {e}")

    # Call validate service
    validate_resp = {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://validate:8002/validate/run",
                json={"batchId": batch_id},
            )
            resp.raise_for_status()
            validate_resp = resp.json()
    except httpx.TimeoutException:
        validate_resp = {"error": "validate service timeout", "batchId": batch_id}
    except httpx.HTTPStatusError as e:
        validate_resp = {"error": f"validate service returned {e.response.status_code}", "batchId": batch_id}
    except httpx.RequestError as e:
        validate_resp = {"error": f"validate service connection failed: {e}", "batchId": batch_id}
    except Exception as e:
        validate_resp = {"error": f"validate call failed: {e}", "batchId": batch_id}

    return {"batchId": batch_id, "filename": safe_filename, "validate": validate_resp}
