from .project import ProjectManager
from .migrations._001_create_projects_table import create_projects_table
from google.cloud import bigquery


class BigQuery:
  client = bigquery.Client()

  def __init__(self):
    self.project = ProjectManager(self.client)

  def run_migrations(self):
    create_projects_table(self.client)
