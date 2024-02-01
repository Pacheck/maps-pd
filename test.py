import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils import queryToGDF

import os


def main():
  subplots: tuple[Figure, Axes] = plt.subplots(figsize=(12, 12))
  fig, eixo = subplots

  queries = [
      # Dados de Estado
      """
      SELECT
      *
      FROM `moss-forest.sources_shp.IBGE_br_estados`
      """,

      # Dados de Municípios
      f"""
      SELECT
      *
      FROM `moss-forest.sources_shp.IBGE_br_municipios`
      WHERE SIGLA = 'AC' OR SIGLA = 'AM'
      """,

      # Dados de área do projeto (área total da propriedade)
      f"""
      SELECT
      *
      FROM `moss-forest.limites_projetos.limites_total_seringueira`
      WHERE project_num = '2'
      """,

      # Dados de AUD
      f"""
      SELECT
      *
      FROM `moss-forest.limites_projetos.Seringueira_v2`
      WHERE project_num = '2'
      """,

      # Zoom do mapa
      """
      SELECT * FROM `moss-forest.sources_shp.zoom_mapa_Seringueira`
      """,

      # Zona do projeto
      """
      SELECT * FROM `moss-forest.sources_shp.zona_projeto_Seringueira`
      """,

      # Vegetação IBGE para o município de interesse
      f"""
      SELECT * FROM `moss-forest.pd_forest.IBGE_vegetacao` a
      JOIN `moss-forest.limites_projetos.seringueira_buffer_200km` b
      ON ST_INTERSECTS((ST_GEOGFROMTEXT(a.geometry, make_valid => True)), (ST_GEOGFROMTEXT(b.geometry, make_valid => True)))
      WHERE ST_INTERSECTION(ST_GEOGFROMTEXT(a.geometry, make_valid => True), (ST_GEOGFROMTEXT(b.geometry, make_valid => True))) IS NOT NULL
      """
  ]

  query = st.sidebar.selectbox('Query', queries)
  if st.sidebar.button('Execute'):
    gdf = queryToGDF(query)

    gdf.boundary.plot(ax=eixo, color="lightgray", linewidth=0.5)

    st.pyplot(fig)


if __name__ == '__main__':
  test()
