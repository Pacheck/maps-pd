import requests
from requests.auth import HTTPBasicAuth
import os
from typing import TypedDict


class Buffer(TypedDict):
  bigQueryId: str
  areaHa: float
  tamanhoKM: float


class Create20And200KmBuffersResponse(TypedDict):
  bigQueryId: str
  areaHa: float
  buffers: list[Buffer]


class ShapefileToPolygonAPI:
  def __init__(self):
    self.api_url = os.getenv('SHAPEFILE_TO_POLYGON_API_URL')
    if not self.api_url:
      raise ValueError('SHAPEFILE_TO_POLYGON_API_URL is not set')
    self.username = os.getenv('SHAPEFILE_TO_POLYGON_USERNAME')
    if not self.username:
      raise ValueError('SHAPEFILE_TO_POLYGON_USERNAME is not set')
    self.password = os.getenv('SHAPEFILE_TO_POLYGON_PASSWORD')
    if not self.password:
      raise ValueError('SHAPEFILE_TO_POLYGON_PASSWORD is not set')

  def create_20_and_200_km_buffers(self, shapefile_url: str):
    response = requests.post(f'{self.api_url}/sync/shapefile-to-polygon', json={
        "shapefileURL": shapefile_url,
        "bufferSizes": [20, 200],
        "shapefileColumnMapper": {
            "geometry": "geometry",
            "areaHa": "Hectares"
        },
        "responseConfig": {
            "ignoreCentroids": True,
            "ignoreGeometries": True
        }
    }, auth=HTTPBasicAuth(self.username, self.password))

    if response.status_code != 200:
      return None

    try:
      json_data = response.json()
      data: Create20And200KmBuffersResponse = json_data['data']
      return data
    except:
      return None
