from google.cloud import bigquery

schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("geometry", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("car", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]


def create_areas_table(client: bigquery.Client):
  table_id = "moss-forest.maps_pd_web.areas"
  table = bigquery.Table(table_id, schema)
  table = client.create_table(table)


def drop_areas_table(client: bigquery.Client):
  table_id = "moss-forest.maps_pd_web.areas"
  client.delete_table(table_id, not_found_ok=True)
