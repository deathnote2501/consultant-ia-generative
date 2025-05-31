from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

# Optional: Add a simple root endpoint for basic verification
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}
