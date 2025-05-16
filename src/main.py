from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.call_handler import app as call_app

app = FastAPI()

app.mount("/", StaticFiles(directory="audios", html=True), name="audios")

app.mount("/voice", call_app)
