from .bigquery import BigQuery
from .bigquery.project import Project
from .bigquery.area import Area, AreaType
from .cloud_storage import CloudStorage
import ibge
from .shapefile_to_polygon import ShapefileToPolygonAPI

bigquery = BigQuery()
cloud_storage = CloudStorage()
shapefile_to_polygon = ShapefileToPolygonAPI()

__all__ = [
    "bigquery",
    "cloud_storage",
    "ibge",
    "shapefile_to_polygon",
    "Area",
    "AreaType",
    "Project"
]
