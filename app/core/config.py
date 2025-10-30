# app/core/config.py (exemplo de local para config centralizada)
import os
from dotenv import load_dotenv

load_dotenv()

# Dados sensíveis
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # default 1 dia

# Conexão com o banco
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# CORS Configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://sgpi.labtecs.com.br,https://api-sgpi.labtecs.com.br,http://api-sgpi.labtecs.com.br,https://sgpi.labtecs.com.br,http://localhost:3000,http://localhost:5173"
).split(",")