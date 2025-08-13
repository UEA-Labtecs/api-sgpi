from datetime import timedelta

DEFAULT_EXPIRATION = timedelta(hours=1)

class StorageService:
    def __init__(self, client_internal, client_public, bucket: str):
        self.client_internal = client_internal
        self.client_public = client_public or client_internal  # fallback
        self.bucket = bucket

    async def upload(self, upload_file, key: str) -> str:
        # grava com o cliente interno
        data = await upload_file.read()
        self.client_internal.put_object(
            self.bucket, key, data=bytes(data), length=len(data), content_type=upload_file.content_type or "application/octet-stream"
        )
        return key

    def delete(self, key: str):
        self.client_internal.remove_object(self.bucket, key)

    def get_presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        # assina com o cliente público (host público)
        return self.client_public.presigned_get_object(
            self.bucket, key, expires=timedelta(seconds=expires_seconds)
        )

def build_storage_from_app(app):
    return StorageService(
        client_internal=app.state.minio_internal,
        client_public=app.state.minio_public,
        bucket=app.state.minio_bucket,
    )
