import uvicorn
from PIserver.server import app

def serve():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    serve()