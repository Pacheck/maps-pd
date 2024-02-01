import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from uuid import uuid4
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as mpatches
import asyncio

from utils import gdf_manager, file_manager, map_manager
from services import bigquery, cloud_storage, ibge, Project, shapefile_to_polygon


class ProjectModel(BaseModel):
  nome: str


@st.cache_data
def get_states_and_cities_data(states: list[str]) -> list[gpd.GeoDataFrame]:
  formatted_states = [f'"{state}"' for state in states]

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
      WHERE sigla IN ({', '.join(formatted_states)})
      """,
  ]

  gdfs = asyncio.run(gdf_manager.batch_async_query(queries))

  return gdfs


@st.cache_data
def get_zone_and_vegetation(zone_buffer_id: str, vegetation_buffer_id: str) -> list[gpd.GeoDataFrame]:
  queries = [
      f"""
      SELECT polygon AS geometry
      FROM `moss-forest.forest.polygons`
      WHERE id = "{zone_buffer_id}"
      """,

      f"""
      SELECT a.geometry, a.legend
      FROM `moss-forest.pd_forest.IBGE_vegetacao` a
      JOIN `moss-forest.forest.polygons` b
      ON ST_INTERSECTS((ST_GEOGFROMTEXT(a.geometry, make_valid => True)), (ST_GEOGFROMTEXT(b.polygon, make_valid => True)))
      WHERE b.id = "{vegetation_buffer_id}"
      AND ST_INTERSECTION(ST_GEOGFROMTEXT(a.geometry, make_valid => True), (ST_GEOGFROMTEXT(b.polygon, make_valid => True))) IS NOT NULL
      """
  ]

  gdfs = asyncio.run(gdf_manager.batch_async_query(queries))

  return gdfs


def main():
  states = ibge.get_states()
  selected_state = st.sidebar.selectbox("Selecione o estado", states)

  border_sharing_states = st.sidebar.multiselect(
      "Selecione o(s) estados que fazem divisa", states[1:])

  cities = ibge.get_cities(selected_state)
  selected_city = st.sidebar.selectbox("Selecione a cidade", cities)

  projects = bigquery.project.list()
  selected_project = st.sidebar.selectbox("Selecione um projeto", projects,
                                          format_func=lambda project: project.name)

  # Criar projeto
  with st.sidebar.expander("Criar projeto"):
    form_data = sp.pydantic_form(key="project_model",
                                 model=ProjectModel, clear_on_submit=True)

    if form_data:
      name = form_data.dict()["nome"]
      project = Project(name)
      bigquery.project.insert(project)
      st.rerun()

  # Upload de arquivos shapefile
  property_area_file = st.sidebar.file_uploader(
      f"Selecione a área da propriedade (.zip)", type="zip")

  aud_file = st.sidebar.file_uploader(
      f"Selecione a área AUD do projeto (.zip)", type="zip")

  # Configurações do Zoom
  zoom_out = st.sidebar.slider("Zoom Out", 0.0, 1.0, 0.0, 0.01)
  zoom_multiplier = 1 + ((zoom_out) * 0.1)

  # Configurações da Seta Norte e Escala
  arrow_north_x, arrow_north_y, arrow_length = 0.91, 0.12, 0.06
  escalaLoc = 'lower right'
  with st.sidebar.expander("Seta Norte"):
    escalaLocOpts = ['lower right',
                     'lower left', 'upper right', 'upper left']
    escalaLoc = st.selectbox('Posição da escala', escalaLocOpts)

    if escalaLoc == 'lower right':
      arrow_north_x, arrow_north_y = 0.91, 0.12
    elif escalaLoc == 'lower left':
      arrow_north_x, arrow_north_y = 0.09, 0.12
    elif escalaLoc == 'upper right':
      arrow_north_x, arrow_north_y = 0.91, 0.94
    elif escalaLoc == 'upper left':
      arrow_north_x, arrow_north_y = 0.09, 0.94

    arrow_north_x = st.slider(
        'Longitude', min_value=0.0, max_value=1.0, value=arrow_north_x)
    arrow_north_y = st.slider(
        'Latitude', min_value=0.0, max_value=1.0, value=arrow_north_y)
    arrow_length = st.slider(
        'Altura da seta', min_value=0.0, max_value=1.0, value=arrow_length)

  # Configurações da Legenda
  legend_x, legend_y = 1.0, 1.01
  with st.sidebar.expander("Legenda"):
    legend_x = st.slider('Longitude', min_value=0.0,
                         max_value=1.2, value=legend_x)
    legend_y = st.slider('Latitude', min_value=0.0,
                         max_value=1.2, value=legend_y)

  # Configurações da Fonte de dados
  data_source_x, data_source_y = 0.81, 0.26
  with st.sidebar.expander("Fonte de dados"):
    data_source_x = st.slider(
        'Longitude', min_value=0.0, max_value=1.0, value=data_source_x)
    data_source_y = st.slider(
        'Latitude', min_value=0.0, max_value=1.0, value=data_source_y)

  # Configurações da Logo
  logo_x1, logo_x2, logo_y1, logo_y2 = 0.81, 0.18, 0.255, 0.04
  with st.sidebar.expander("Logo"):
    logo_x1 = st.slider('Longitude do 1° canto do retângulo',
                        min_value=0.0, max_value=1.0, value=logo_x1)
    logo_x2 = st.slider('Latitude do 1° canto do retângulo',
                        min_value=0.0, max_value=1.0, value=logo_x2)
    logo_y1 = st.slider('Longitude do 3° canto do retângulo',
                        min_value=0.0, max_value=1.0, value=logo_y1)
    logo_y2 = st.slider('Latitude do 3° canto do retângulo',
                        min_value=0.0, max_value=1.0, value=logo_y2)

  if st.sidebar.button("Gerar mapa"):
    errors: list[str] = []

    if not selected_state:
      errors.append("Selecione um estado")

    if not selected_city:
      errors.append("Selecione uma cidade")

    if not selected_project:
      errors.append("Selecione um projeto")

    if not property_area_file:
      errors.append("Selecione um arquivo para a área da propriedade")

    if not aud_file:
      errors.append("Selecione um arquivo para a área AUD")

    if len(errors):
      for error in errors:
        st.error(error)
      return

    all_selected_states: list[str] = list(
        set(border_sharing_states + [selected_state]))

    uf_gdf, mun_gdf = get_states_and_cities_data(all_selected_states)

    subplots: tuple[Figure, Axes] = plt.subplots(figsize=(12, 12))
    fig, axes = subplots
    legend_elements: list[mpatches.Rectangle] = []

    # Get property area GeoDataFrame
    property_area_file_path = file_manager.save_file(property_area_file)

    blob = cloud_storage.upload_to_bucket(
        property_area_file_path)

    property_area_gdf: gpd.GeoDataFrame = gpd.read_file(
        property_area_file_path)
    property_area_gdf = gdf_manager.format(property_area_gdf)

    file_manager.delete_file(property_area_file_path)

    # Get Project area AUD GeoDataFrame
    aud_file_path = file_manager.save_file(aud_file)

    aud_gdf: gpd.GeoDataFrame = gpd.read_file(aud_file_path)
    aud_gdf = gdf_manager.format(aud_gdf)

    file_manager.delete_file(aud_file_path)

    # Use zoom para definir limites do mapa e transformar em um quadrado
    minx, miny, maxx, maxy = map_manager.set_area_total_bounds(
        property_area_gdf.total_bounds, zoom_multiplier)

    axes.set_ylim(miny, maxy)
    axes.set_xlim(minx, maxx)

    buffers_response = shapefile_to_polygon.create_20_and_200_km_buffers(
        blob['url'])

    if not buffers_response:
      return st.error("Erro ao criar buffers")

    buffers = buffers_response['buffers']

    zone_buffer_id = ""
    vegetation_buffer_id = ""

    for buffer in buffers:
      if buffer['tamanhoKM'] == 20:
        zone_buffer_id = buffer['bigQueryId']
      elif buffer['tamanhoKM'] == 200:
        vegetation_buffer_id = buffer['bigQueryId']

    zona_gdf, vege_gdf = get_zone_and_vegetation(
        zone_buffer_id, vegetation_buffer_id)

    legend_colors = {
        'Property Area': '#000000',
        'Project Area AUD': '#FF1493',
        'State Boundaries': '#D3D3D3',
        'Municipal Boundaries': '#000000',
    }

    # Denifir as cores das classes de vegetação
    vegetation_legends = vege_gdf['legend'].unique()
    vegetation_color_options = ["#0000ff", "#00FF4B",
                                "#2F4F4F", "#3CB371", "#556B2F", "#808000", "#808080",
                                "#84FF4C", "#98FB98", "#ADFFB0", "#C8FFB0", "#ffff00"]
    for i, vegetation_legend in enumerate(vegetation_legends):
      legend_colors[vegetation_legend] = vegetation_color_options[i %
                                                                  len(vegetation_color_options)]

    # Paleta de cores
    with st.sidebar.expander("Paleta de cores"):
      for key, color in legend_colors.items():
        legend_colors[key] = st.color_picker(key, color)

    # Desenhar polígonos no mapa
    property_area_gdf.boundary.plot(ax=axes, color=legend_colors["Property Area"],
                                    linewidth=1.3, linestyle='--')
    aud_gdf.boundary.plot(
        ax=axes, color=legend_colors["Project Area AUD"], linewidth=1.3, hatch='//')
    vege_gdf.boundary.plot(ax=axes, color="lightgray", linewidth=0.5)
    uf_gdf.boundary.plot(
        ax=axes, color=legend_colors['State Boundaries'], linewidth=4)
    mun_gdf.boundary.plot(
        ax=axes, color=legend_colors['Municipal Boundaries'], linewidth=0.5)

    # Legendas dos polígonos
    legend_elements.append(mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor=legend_colors["Property Area"], linewidth=1.3, linestyle='--', label='Property Area'))
    legend_elements.append(
        mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False, edgecolor=legend_colors["Project Area AUD"],
                           linewidth=1.3, hatch='//', label='Project Area AUD'))
    legend_elements.append(
        mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False,
                           edgecolor=legend_colors["State Boundaries"], linewidth=4, label='State Boundaries'))
    legend_elements.append(
        mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False,
                           edgecolor=legend_colors["Municipal Boundaries"], linewidth=0.5, label='Municipal Boundaries'))

    # Legendas das classes de vegetação
    for vegetation_legend in vegetation_legends:
      data = vege_gdf[vege_gdf.legend == vegetation_legend]
      if data.intersects(zona_gdf.unary_union).any():
        color = legend_colors[vegetation_legend]

        legend_elements.append(mpatches.Rectangle(
            (0, 0), 0.1, 0.1, facecolor=color, edgecolor='black', label=vegetation_legend))

        data.plot(ax=axes, color=color, linewidth=1.3, label=vegetation_legend)

    # Posicione a legenda
    plt.legend(handles=legend_elements, bbox_to_anchor=(
        legend_x, legend_y), loc='upper left', fontsize=9)

    # Adicione rótulos aos polígonos dentro do eixo
    for x, y, label in zip(mun_gdf.geometry.centroid.x, mun_gdf.geometry.centroid.y, mun_gdf["NM_MUN"]):
      if minx < x < maxx and miny < y < maxy:
        axes.annotate(label, (x, y), xytext=(
            3, 3), textcoords="offset points", fontsize=9, ha='center', va='center')

    # Defina o estilo dos rótulos do eixo
    axes.ticklabel_format(style="plain")

    # Rotacione os rótulos do eixo y em 90 graus
    axes.set_yticklabels(axes.get_yticks(), rotation=90)
    axes.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

    # Escala
    axes.add_artist(ScaleBar(dx=1, location=escalaLoc))

    # Seta Norte
    axes.annotate('N', xy=(arrow_north_x, arrow_north_y), xytext=(arrow_north_x, arrow_north_y-arrow_length),
                  arrowprops=dict(facecolor='black', width=5, headwidth=15),
                  ha='center', va='center', fontsize=13,
                  xycoords=axes.transAxes)

    # Carregue a logo PNG ou JPEG
    logo_path = './data/images/terra-vista-logo.jpg'
    logo = plt.imread(logo_path)

    # Crie um novo eixo para a logo abaixo do texto Source
    logo_axes: Axes = fig.add_axes([logo_x1, logo_x2, logo_y1, logo_y2])

    # Plote a logo no novo eixo
    logo_axes.imshow(logo, aspect='auto')

    # Desative os eixos (ticks e labels) para o novo eixo da logo
    logo_axes.set_axis_off()

    # Ajuste conforme necessário
    plt.subplots_adjust(right=0.8)

    # Adicione o texto da fonte fora da figura
    fonte = f"SIRGAS 2000 / UTM zone 19S \nSource: Vegetation Map 1:250.000 (IBGE, 2021) \nVersion: 13/12/2023 \nMunicipality/St.: {selected_city}/{selected_state}"
    fig.text(data_source_x, data_source_y, fonte, va='center', fontsize=9, bbox=dict(
        boxstyle='round,pad=0.3', edgecolor='lightgray', facecolor='white'))

    st.pyplot(fig)


if __name__ == "__main__":
  main()
