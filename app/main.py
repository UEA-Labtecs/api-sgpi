from fastapi import FastAPI
from app.core.minioClient import init_minio
from app.routes import auth, dashboard, patent, userPatentStage
from app.core.database import Base, engine
from app.core.config import CORS_ORIGINS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Crawler INPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(patent.router)
app.include_router(dashboard.router) 
app.include_router(userPatentStage.router)

@app.on_event("startup")
def _startup():
    init_minio(app)
    
@app.get("/ping")
def ping():
    return {"message": "pong"}
