from google.cloud import bigquery
from .constants import tables


class Project:
  id: str
  name: str

  def __init__(self, id: str, name: str):
    self.id = id
    self.name = name


class ProjectManager:
  def __init__(self, client: bigquery.Client):
    self.client = client

  def insert(self, project: Project):
    query_str = f"""
                    INSERT INTO `{tables['projects']}` (id, name)
                    VALUES ("{project.id}", "{project.name}")
                    """
    self.client.query(query_str).result()

  def list(self):
    query_str = f"""
                    SELECT * FROM `{tables['projects']}`
                    """
    results = self.client.query(query_str).result()

    projects = [Project(r["id"], r["name"]) for r in results]

    return projects
