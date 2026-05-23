from sqlmodel import SQLModel, Session, create_engine 

DATABASE_URL = "sqlite:///./database.db" # aqui salva o endereço do banco de dados

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # aqui cria a conexão, a chave para abrir o banco de dados

# função para criar tabelas quando o servidor subir
def create_db_and_tables(): 
    SQLModel.metadata.create_all(engine) # aqui ele mostra a rota aonde deve passar, usa o engine como chave para registrar no .db

# função para criar a session 
def get_session(): 
    with Session(engine) as session:
        yield session # antes do yield é abrir a sessão, depois é fechar