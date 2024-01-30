import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from uuid import uuid4
from services import bigquery, Project
from utils import save_file, delete_file
import geopandas as gpd
import matplotlib.pyplot as plt


class ProjectModel(BaseModel):
  nome: str


def main():
  projects = bigquery.project.list()
  selected_project = st.sidebar.selectbox("Selecione um projeto", projects,
                                          format_func=lambda project: project.name)

  with st.sidebar.expander("Criar projeto"):
    data = sp.pydantic_form(key="project_model",
                            model=ProjectModel, clear_on_submit=True)

    if data:
      id = uuid4()
      parsed_data = data.dict()
      name = parsed_data["nome"]
      project = Project(id, name)
      bigquery.project.insert(project)
      st.experimental_rerun()

  file = st.sidebar.file_uploader(f"Selecione um arquivo (.zip)", type="zip")

  if st.sidebar.button("Gerar mapa"):
    errors: list[str] = []

    if not selected_project:
      errors.append("Selecione um projeto")

    if not file:
      errors.append("Selecione um arquivo")

    if len(errors):
      st.sidebar.error("\n".join(errors))
      return

    file_path = save_file(file)
    gdf: gpd.GeoDataFrame = gpd.read_file(file_path)
    delete_file(file_path)

    fig, eixo = plt.subplots(figsize=(12, 12))

    # Limites dos polígonos da área do projeto
    gdf.boundary.plot(ax=eixo, color="black",
                      linewidth=1.3, linestyle='--')

    area_do_projeto_geometry = gdf.geometry

    # Explode the MULTIPOLYGON into separate POLYGONS
    gdf_exploded = gdf.explode()
    gdf_exploded = gdf_exploded.reset_index(drop=True)

    for row in gdf_exploded.iterrows():
      print(row)
      print("\n\n")

    st.pyplot(fig)


if __name__ == "__main__":
  main()
