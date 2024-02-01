from google.cloud import bigquery
from datetime import datetime
from uuid import uuid4

from .constants import tables


class Project:
  id: str
  name: str
  created_at: datetime

  def __init__(self, name: str, id: str = None, created_at: datetime = None):
    if not id:
      id = uuid4()

    if not created_at:
      created_at = datetime.now()

    self.id = id
    self.name = name
    self.created_at = created_at


class ProjectManager:
  def __init__(self, client: bigquery.Client):
    self.client = client

  def insert(self, project: Project):
    query_str = f"""
                INSERT INTO `{tables['projects']}` (id, name, created_at)
                VALUES ("{project.id}", "{project.name}", CURRENT_TIMESTAMP())
                """
    self.client.query(query_str).result()

  def list(self):
    query_str = f"""
                SELECT * FROM `{tables['projects']}`
                """
    results = self.client.query(query_str).result()

    projects = [Project(r["name"], r["id"],  r["created_at"]) for r in results]

    return projects
