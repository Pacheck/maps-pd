from .project import ProjectManager
from .area import AreaManager
from .migrations._001_create_projects_table import create_projects_table, drop_projects_table
from .migrations._002_create_areas_table import create_areas_table, drop_areas_table
from google.cloud import bigquery


class BigQuery:
  client = bigquery.Client()

  def __init__(self):
    self.project = ProjectManager(self.client)
    self.area = AreaManager(self.client)

  def run_migrations(self):
    drop_areas_table(self.client)
    drop_projects_table(self.client)
    create_projects_table(self.client)
    create_areas_table(self.client)
    return self
