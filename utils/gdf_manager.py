import asyncio
import geopandas as gpd
from shapely.wkt import loads
from google.cloud import bigquery

client = bigquery.Client(project='moss-forest')


def format(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
  return gdf.to_crs(crs='EPSG:31979')


def query(q: str) -> gpd.GeoDataFrame:
  query_job = client.query(q)
  df = query_job.to_dataframe()
  df['geometry'] = df['geometry'].apply(loads)
  gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
  gdf = format(gdf)
  return gdf


async def async_query(q: str) -> gpd.GeoDataFrame:
  loop = asyncio.get_event_loop()
  gdf = await loop.run_in_executor(None, query, q)
  return gdf


async def batch_async_query(queries: list[str]) -> list[gpd.GeoDataFrame]:
  tasks = (async_query(q) for q in queries)
  gdfs = await asyncio.gather(*tasks)
  return gdfs
