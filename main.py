import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test message from FastAPI server"}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=4000, debug=False)
