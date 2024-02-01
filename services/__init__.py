from .bigquery import BigQuery
from .cloud_storage import CloudStorage
from .shapefile_to_polygon import ShapefileToPolygonAPI

bigquery = BigQuery()
cloud_storage = CloudStorage()
shapefile_to_polygon = ShapefileToPolygonAPI()

__init__ = [
    "bigquery",
    "cloud_storage",
    "shapefile_to_polygon"
]
