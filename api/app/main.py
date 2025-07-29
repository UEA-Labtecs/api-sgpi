from fastapi import FastAPI
from app.routes import auth, patent
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Crawler INPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou restrinja para seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(patent.router)

@app.get("/ping")
def ping():
    return {"message": "pong"}
