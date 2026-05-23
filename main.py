from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import produtos, usuarios

app = FastAPI()

app.include_router(produtos.router)
app.include_router(usuarios.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()