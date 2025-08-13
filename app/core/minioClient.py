import os
from minio import Minio
from minio.error import S3Error
from fastapi import FastAPI

def get_minio_client() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

def init_minio(app: FastAPI):
    client = get_minio_client()
    bucket = os.getenv("MINIO_BUCKET", "sgpi-files")
    region = os.getenv("MINIO_REGION", None)

    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket, location=region) if region else client.make_bucket(bucket)
    # Opcional: política pública só de leitura (se quiser links públicos):
    # from minio.commonconfig import Policy
    # client.set_bucket_policy(bucket, policy_json_string)

    # guardar na app.state para reuso
    app.state.minio = client
    app.state.minio_bucket = bucket
