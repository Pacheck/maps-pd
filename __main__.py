import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from uuid import uuid4
from services import bigquery, Project
from utils import save_file, delete_file
import geopandas as gpd


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

  file = st.sidebar.file_uploader("Selecione um arquivo (.zip)", type="zip")

  if st.sidebar.button("Gerar mapa"):
    if file is None:
      return st.sidebar.error("Selecione um arquivo")

    file_path = save_file(file)
    gdf = gpd.read_file(file_path)
    delete_file(file_path)
    print(gdf.head())


main()
