from google.cloud import bigquery
from .constants import tables
from datetime import datetime


class Project:
  id: str
  name: str
  created_at: datetime

  def __init__(self, id: str, name: str, created_at: datetime = None):
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

    projects = [Project(r["id"], r["name"], r["created_at"]) for r in results]

    return projects
