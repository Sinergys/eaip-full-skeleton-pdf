from fastapi import FastAPI

app = FastAPI(title="EAIP management", version="0.1.0")


@app.get("/health")
def health():
    return {"service": "management", "status": "ok"}
