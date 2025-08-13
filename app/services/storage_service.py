from datetime import timedelta
import io
import os
import time
from typing import Optional
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from starlette.datastructures import UploadFile as StarletteUploadFile

DEFAULT_EXPIRATION = timedelta(hours=1)

class StorageService:
    def __init__(self, client: Minio, bucket: str):
        self.client = client
        self.bucket = bucket

    async def upload(self, file: UploadFile, key: str) -> str:
        # lê o arquivo do UploadFile
        content = await file.read()
        data = io.BytesIO(content)
        size = len(content)
        content_type = file.content_type or "application/octet-stream"

        # faz upload
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=key,
            data=data,
            length=size,
            content_type=content_type,
        )
        # Retorne a key (ou uma URL assinada, se preferir)
        return key

    def get_presigned_url(self, key: str, expires: int = DEFAULT_EXPIRATION) -> str:
        return self.client.presigned_get_object(self.bucket, key, expires=expires)

    def delete(self, key: str) -> None:
        self.client.remove_object(self.bucket, key)

    def exists(self, key: str) -> bool:
        try:
            self.client.stat_object(self.bucket, key)
            return True
        except S3Error:
            return False

# Factory helper
def build_storage_from_app(app) -> StorageService:
    return StorageService(client=app.state.minio, bucket=app.state.minio_bucket)
