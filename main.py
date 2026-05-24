from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import usuarios, itens, chamado

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(itens.router)
app.include_router(chamado.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()