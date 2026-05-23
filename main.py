from fastapi import FastAPI
from app.routers import produtos

app = FastAPI()          # ← Uvicorn encontra esse objeto
app.include_router(produtos.router)