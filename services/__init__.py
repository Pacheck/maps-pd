from .ibge import IBGE
from .bigquery import BigQuery
from .bigquery.project import Project
from .bigquery.area import Area, AreaType

ibge = IBGE()
bigquery = BigQuery()

__all__ = [
    "ibge",
    "bigquery",
    "Project",
    "Area",
    "AreaType"
]
