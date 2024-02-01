import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from uuid import uuid4
from matplotlib.figure import Figure
from io import BytesIO

cwd = os.getcwd()

tmp_folder = os.path.join(cwd, 'tmp')


def delete_file(file_path: str) -> None:
  if os.path.exists(file_path):
    os.remove(file_path)


def convert_fig_to_bytes(fig: Figure) -> str:
  buf = BytesIO()
  fig.savefig(buf, format='png')
  buf.seek(0)
  return buf


def read_file(file_path: str) -> bytes:
  with open(file_path, "rb") as f:
    return f.read()


def save_file(file: UploadedFile) -> str:
  ext = file.name.split('.')[-1]
  file_name = f"{uuid4()}.{ext}"

  file_path = os.path.join(tmp_folder, file_name)

  with open(file_path, "wb") as f:
    f.write(file.getbuffer())

  return file_path
