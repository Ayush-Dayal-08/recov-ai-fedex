from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Recov-AI Backend Running", "project": "FedEx SMART Hackathon"}
