from fastapi import FastAPI
from .routers import chat, health


app = FastAPI()

app.include_router(chat.router)
app.include_router(health.router)
