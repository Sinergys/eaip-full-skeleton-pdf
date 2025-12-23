from fastapi import FastAPI

app = FastAPI(title="EAIP gateway-auth", version="0.1.0")


@app.get("/health")
def health():
    return {"service": "gateway-auth", "status": "ok"}
