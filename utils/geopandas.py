import asyncio
import geopandas as gpd
from shapely.wkt import loads
from google.cloud import bigquery

client = bigquery.Client(project='moss-forest')


def queryToGDF(query: str) -> gpd.GeoDataFrame:
  query_job = client.query(query)
  df = query_job.to_dataframe()
  df['geometry'] = df['geometry'].apply(loads)
  gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
  gdf = gdf.to_crs(crs='EPSG:31979')
  return gdf


async def asyncQueryToGDF(query: str) -> gpd.GeoDataFrame:
  loop = asyncio.get_event_loop()
  gdf = await loop.run_in_executor(None, queryToGDF, query)
  return gdf


async def batchAsyncQueryToGDF(queries: list[str]) -> list[gpd.GeoDataFrame]:
  tasks = (asyncQueryToGDF(query) for query in queries)
  gdfs = await asyncio.gather(*tasks)
  return gdfs
