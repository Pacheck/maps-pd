from .ibge import IBGE
from .bigquery import BigQuery
from .bigquery.project import Project

ibge = IBGE()
bigquery = BigQuery()

__all__ = [
    "ibge",
    "bigquery",
    "Project"
]
