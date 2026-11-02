from fastapi import FastAPI

HOST = "127.0.0.1"
PORT = 8001


def run(application: FastAPI) -> None:
    import uvicorn

    uvicorn.run(application, host=HOST, port=PORT)
