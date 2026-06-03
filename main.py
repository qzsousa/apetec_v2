from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import usuarios, itens, chamado, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(itens.router)
app.include_router(chamado.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],  # origem do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)