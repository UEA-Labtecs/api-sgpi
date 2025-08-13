import os
from minio import Minio

def init_minio(app):
    # interno (para I/O)
    endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = str(os.getenv("MINIO_SECURE", "false")).lower() in ("1","true","yes")
    bucket = os.getenv("MINIO_BUCKET", "sgpi-files")

    client_internal = Minio(endpoint, access_key=access, secret_key=secret, secure=secure)

    # garante bucket usando o cliente interno
    if not client_internal.bucket_exists(bucket):
        client_internal.make_bucket(bucket)

    # público (apenas para assinar URLs)
    pub_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT")
    pub_secure = str(os.getenv("MINIO_PUBLIC_SECURE", "true")).lower() in ("1","true","yes")

    client_public = None
    if pub_endpoint:
        client_public = Minio(pub_endpoint, access_key=access, secret_key=secret, secure=pub_secure)

    app.state.minio_internal = client_internal
    app.state.minio_public = client_public
    app.state.minio_bucket = bucket
