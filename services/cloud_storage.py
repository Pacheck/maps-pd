from google.cloud import storage
from datetime import timedelta
import os
from typing import TypedDict


class UploadToBucketResponse(TypedDict):
  url: str
  blob_name: str


class CloudStorage:
  def __init__(self):
    self.storage_client = storage.Client()
    self.bucket_name: str = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET_NAME")
    if not self.bucket_name:
      raise Exception(
          "GOOGLE_CLOUD_STORAGE_BUCKET_NAME not found in environment variables.")
    self.folder_path: str = os.getenv("GOOGLE_CLOUD_STORAGE_FOLDER_PATH")
    if not self.folder_path:
      raise Exception(
          "GOOGLE_CLOUD_STORAGE_FOLDER_PATH not found in environment variables.")

  def upload_to_bucket(self, file_path: str) -> UploadToBucketResponse:
    bucket = self.storage_client.bucket(self.bucket_name)
    blob_name = f"{self.folder_path}/{os.path.basename(file_path)}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    response: UploadToBucketResponse = {
        'url': f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}",
        'blob_name': blob_name,
    }
    return response

  def delete_from_bucket(self, blob_name: str) -> None:
    bucket = self.storage_client.bucket(self.bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
