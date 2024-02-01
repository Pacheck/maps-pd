import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from uuid import uuid4

cwd = os.getcwd()


def delete_file(file_path: str) -> None:
  if os.path.exists(file_path):
    os.remove(file_path)


def save_file(file: UploadedFile) -> str:
  ext = file.name.split('.')[-1]
  file_name = f"{uuid4()}.{ext}"

  file_path = os.path.join(cwd, 'tmp', file_name)

  with open(file_path, "wb") as f:
    f.write(file.getbuffer())

  return file_path
