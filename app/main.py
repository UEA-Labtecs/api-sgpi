from fastapi import FastAPI
from app.routes import auth, patent
from app.core.database import Base, engine

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Crawler INPI", version="1.0.0")

app.include_router(auth.router)
app.include_router(patent.router)
