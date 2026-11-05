from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import secretaria, usuarios, itens, chamado, auth, notificacoes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "https://apetec-v2.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(itens.router)
app.include_router(chamado.router)
app.include_router(auth.router)
app.include_router(secretaria.router)
app.include_router(notificacoes.router)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/login.html")
def login():
    return FileResponse("frontend/login.html")

@app.get("/dashboard.html")
def dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/register.html")
def register():
    return FileResponse("frontend/register.html")

@app.get("/recuperar-senha.html")
def recuperar_senha_page():
    return FileResponse("frontend/recuperar-senha.html")

@app.get("/dashboard-secretaria.html")
def dashboard_secretaria():
    return FileResponse("frontend/dashboard-secretaria.html")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
