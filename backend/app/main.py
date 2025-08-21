from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return 'hello'

@app.get("/api/health")
def health():
    return {"ok": True, "service": "ab-test-backend"}