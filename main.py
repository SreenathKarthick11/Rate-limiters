from fastapi import FastAPI,Depends
from middleware.middleware import rate_limit
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/limited")
def limited( _ = Depends(rate_limit(capacity=5, refill_rate=0.5))):
    return {"status": "limited access granted"}