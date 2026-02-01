# uvicorn main:app --reload to run the server

from fastapi import FastAPI,Depends
from middleware.middleware import rate_limit
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/token_bucket")
def limited( _ = Depends(rate_limit(type="token_bucket", capacity=5, rate=0.5))):
    return {"status": "limited access granted"}

@app.get("/leaky_bucket")
def limited( _ = Depends(rate_limit(type="leaky_bucket", capacity=5, rate=0.5))):
    return {"status": "limited access granted"}

@app.get("/fixed_window_counter")
def limited( _ = Depends(rate_limit(type="fixed_window_counter", capacity=5,window_size=10))):
    return {"status": "limited access granted"}