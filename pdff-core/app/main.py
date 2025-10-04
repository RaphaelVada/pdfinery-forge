from fastapi import FastAPI

app = FastAPI(title="PDFF Core")

@app.get("/")
def root():
    return {"message": "PDFF Core running"}

@app.get("/health")
def health():
    return {"status": "okey"}