from google.cloud import bigquery
from .constants import tables
from datetime import datetime
from enum import Enum


class AreaType(Enum):
  PROJECT_AREA = "area_do_projeto"
  AUD = "area_do_aud"
  APD = "area_do_apd"


class Area:
  id: str
  project_id: str
  type: AreaType
  geometry: str
  car: str
  created_at: datetime

  def __init__(
      self,
      id: str,
      project_id: str,
      type: AreaType,
      geometry: str,
      car: str,
      created_at: datetime = None
  ):
    self.id = id
    self.project_id = project_id
    self.type = type
    self.geometry = geometry
    self.car = car
    self.created_at = created_at


class AreaManager:
  def __init__(self, client: bigquery.Client):
    self.client = client

  def insert(self, area: Area):
    query_str = f"""
                INSERT INTO `{tables['areas']}` (id, project_id, type, geometry, car, created_at)
                VALUES ("{area.id}", "{area.project_id}", "{area.type}", "{area.geometry}", "{area.car}", CURRENT_TIMESTAMP())
                """
    self.client.query(query_str).result()

  def get_by_id(self, id: str):
    query_str = f"""
                SELECT * FROM `{tables['areas']}`
                WHERE id = "{id}"
                LIMIT 1
                """
    results = self.client.query(query_str).result()

    if results.total_rows == 0:
      return None

    r = results[0]

    area = Area(r["id"], r["project_id"], r["type"], r["geometry"],
                r["car"], r["created_at"])

    return area

  def list_by_project_id(self, project_id: str):
    query_str = f"""
                SELECT * FROM `{tables['areas']}`
                WHERE project_id = "{project_id}"
                """
    results = self.client.query(query_str).result()

    areas = [Area(r["id"], r["project_id"], r["type"], r["geometry"],
                  r["car"], r["created_at"]) for r in results]

    return areas

  def list(self):
    query_str = f"""
                SELECT * FROM `{tables['areas']}`
                """
    results = self.client.query(query_str).result()

    areas = [Area(r["id"], r["project_id"], r["type"], r["geometry"],
                  r["car"], r["created_at"]) for r in results]

    return areas
