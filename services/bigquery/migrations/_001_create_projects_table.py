from google.cloud import bigquery

schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]


def create_projects_table(client: bigquery.Client):
  table_id = "moss-forest.maps_pd_web.projects"
  table = bigquery.Table(table_id, schema)
  table = client.create_table(table)


def drop_projects_table(client: bigquery.Client):
  table_id = "moss-forest.maps_pd_web.projects"
  client.delete_table(table_id, not_found_ok=True)
