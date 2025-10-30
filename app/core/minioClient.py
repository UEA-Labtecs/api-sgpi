import os
from urllib.parse import urlparse
from minio import Minio

def _parse_endpoint(endpoint_str):
    """Parse endpoint URL to extract hostname:port and determine secure flag."""
    if not endpoint_str:
        return None, None, None, False
    
    # If it's already in hostname:port format, return as is
    if "://" not in endpoint_str:
        # Check if port is included
        parts = endpoint_str.split(":", 1)
        if len(parts) == 2:
            return endpoint_str, parts[0], int(parts[1]), False
        return endpoint_str, endpoint_str, None, False
    
    # Parse URL format (http://hostname:port or https://hostname:port)
    parsed = urlparse(endpoint_str)
    hostname = parsed.hostname
    port = parsed.port
    secure = parsed.scheme == "https"
    
    # Build hostname:port string for MinIO client
    if port:
        endpoint = f"{hostname}:{port}"
    else:
        endpoint = hostname
    
    return endpoint, hostname, port, secure

def init_minio(app):
    # interno (para I/O)
    endpoint_raw = os.getenv("MINIO_ENDPOINT", "minio:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    
    # Parse endpoint and determine secure flag
    endpoint, hostname, port, secure_from_url = _parse_endpoint(endpoint_raw)
    
    # Allow explicit override of secure flag via env var
    secure_env = os.getenv("MINIO_SECURE")
    if secure_env:
        secure = str(secure_env).lower() in ("1","true","yes")
    else:
        secure = secure_from_url if secure_from_url is not None else False
    
    bucket = os.getenv("MINIO_BUCKET", "sgpi-files")

    # Log para debug (sem expor senha completa)
    print(f"[minio] Conectando ao MinIO: {endpoint} (secure={secure})")
    print(f"[minio] Bucket: {bucket}")
    print(f"[minio] Access Key: {access[:8]}...")
    
    try:
        client_internal = Minio(endpoint, access_key=access, secret_key=secret, secure=secure)
        
        # garante bucket usando o cliente interno
        try:
            if not client_internal.bucket_exists(bucket):
                print(f"[minio] Bucket {bucket} não existe, criando...")
                client_internal.make_bucket(bucket)
                print(f"[minio] ✅ Bucket {bucket} criado")
            else:
                print(f"[minio] ✅ Bucket {bucket} existe")
        except Exception as e:
            print(f"[minio] ❌ Erro ao verificar/criar bucket: {e}")
            raise
    except Exception as e:
        print(f"[minio] ❌ Erro ao conectar ao MinIO: {e}")
        print(f"[minio] Endpoint: {endpoint}")
        print(f"[minio] Secure: {secure}")
        raise

    # público (apenas para assinar URLs)
    pub_endpoint_raw = os.getenv("MINIO_PUBLIC_ENDPOINT")
    client_public = None
    if pub_endpoint_raw:
        pub_endpoint_parsed, _, _, pub_secure_from_url = _parse_endpoint(pub_endpoint_raw)
        
        # Allow explicit override of secure flag via env var
        pub_secure_env = os.getenv("MINIO_PUBLIC_SECURE")
        if pub_secure_env:
            pub_secure = str(pub_secure_env).lower() in ("1","true","yes")
        else:
            pub_secure = pub_secure_from_url if pub_secure_from_url is not None else True
        
        client_public = Minio(pub_endpoint_parsed, access_key=access, secret_key=secret, secure=pub_secure)

    app.state.minio_internal = client_internal
    app.state.minio_public = client_public
    app.state.minio_bucket = bucket
