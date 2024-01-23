from google.cloud import bigquery

schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
]


def create_projects_table(client: bigquery.Client):
  table_id = "moss-forest.maps_pd_web.projects"
  table = bigquery.Table(table_id, schema=schema)
  table = client.create_table(table)
