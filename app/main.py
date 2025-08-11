from fastapi import FastAPI
from app.routes import auth, dashboard, patent
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Crawler INPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(patent.router)
app.include_router(dashboard.router) 

@app.get("/ping")
def ping():
    return {"message": "pong"}
