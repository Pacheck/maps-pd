import streamlit as st
from utils import batchAsyncQueryToGDF
import asyncio
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st


@st.cache_data
def loadVegetationData(estado: str, project_num: str):
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
      WHERE SIGLA = 'AC' OR SIGLA = '{estado}'
      """,

      # Dados de área do projeto (área total da propriedade)
      f"""
      SELECT
      *
      FROM `moss-forest.limites_projetos.limites_total_seringueira`
      where project_num = '{project_num}'
      """,

      # Dados de AUD
      f"""
      SELECT
      *
      FROM `moss-forest.limites_projetos.Seringueira_v2`
      where project_num = '{project_num}'
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

  gdfs = asyncio.run(batchAsyncQueryToGDF(queries))

  return gdfs


def buildVegetationMap(municipio: str, estado: str, project_num: str):
  paleta = {}
  paleta_vege_default_colors = [
      ("Alluvial Open Ombrophilous Forest", "#C8FFB0"),
      ("Lowland Open Ombrophilous Forest", '#ADFFB0'),
      ("Alluvial Dense Ombrophilous Forest", "#84FF4C"),
      ("Lowland Dense Ombrophilous Forest", "#00FF4B"),
      ("Urban Influence", '#808080'),
      ("Continental Water Body", '#0000ff'),
      ("Livestock Pastures", '#ffff00'),
      ("Submontane Dense Ombrophilous Forest", '#2F4F4F'),
      ("Wooded Campinarana", '#98FB98'),
      ("Secondary Vegetation", '#3CB371'),
      ("Pioneer Formation with Fluvial and/or Lacustrine Influence", '#808000'),
      ("Grassy Wooded Campinarana", '#556B2F')
  ]

  with st.sidebar.expander("Paleta de cores"):
    for key, color in paleta_vege_default_colors:
      paleta[key] = st.color_picker(key, color)

  uf_gdf, mun_gdf, areaproj_gdf, aud, zoom_gdf, zona_gdf, vege_gdf = loadVegetationData(
      estado, project_num)

  # Configurações da Seta Norte e Escala
  xn, yn, arrow_length = 0.91, 0.12, 0.06
  escalaLoc = 'lower right'
  with st.sidebar.expander("Seta Norte"):
    escalaLocOpts = ['lower right',
                     'lower left', 'upper right', 'upper left']
    escalaLoc = st.selectbox('Posição da escala', escalaLocOpts)

    if escalaLoc == 'lower right':
      xn, yn = 0.91, 0.12
    elif escalaLoc == 'lower left':
      xn, yn = 0.09, 0.12
    elif escalaLoc == 'upper right':
      xn, yn = 0.91, 0.94
    elif escalaLoc == 'upper left':
      xn, yn = 0.09, 0.94

    xn = st.slider('Longitude', min_value=0.0, max_value=1.0, value=xn)
    yn = st.slider('Latitude', min_value=0.0, max_value=1.0, value=yn)
    arrow_length = st.slider(
        'Altura da seta', min_value=0.0, max_value=1.0, value=arrow_length)

  # Configurações da Legenda
    legendaX = 1.0
    legendaY = 1.01
  with st.sidebar.expander("Legenda"):
    legendaX = st.slider('Longitude', min_value=0.0,
                         max_value=1.2, value=legendaX)
    legendaY = st.slider('Latitude', min_value=0.0,
                         max_value=1.2, value=legendaY)

  # Configurações da Fonte de dados
  xData, yData = 0.81, 0.26
  with st.sidebar.expander("Fonte de dados"):
    xData = st.slider('Longitude', min_value=0.0, max_value=1.0, value=xData)
    yData = st.slider('Latitude', min_value=0.0, max_value=1.0, value=yData)

  # Configurações da Logo
  x1Logo, y1Logo, x2Logo, y2Logo = 0.81, 0.18, 0.255, 0.04
  with st.sidebar.expander("Logo"):
    x1Logo = st.slider('Longitude do 1° canto do retângulo',
                       min_value=0.0, max_value=1.0, value=x1Logo)
    y1Logo = st.slider('Latitude do 1° canto do retângulo',
                       min_value=0.0, max_value=1.0, value=y1Logo)
    x2Logo = st.slider('Longitude do 3° canto do retângulo',
                       min_value=0.0, max_value=1.0, value=x2Logo)
    y2Logo = st.slider('Latitude do 3° canto do retângulo',
                       min_value=0.0, max_value=1.0, value=y2Logo)

  # Classes de Vegetação
  valores_unicos = vege_gdf['legend'].unique()

  # Vegetation types in the Seringueira project area
  minx, miny, maxx, maxy = zoom_gdf.total_bounds
  # Crie a figura e o eixo de plotagem. Defina o tamanho da figura
  fig, eixo = plt.subplots(figsize=(12, 12))
  # Limites dos polígonos da área do projeto
  areaproj_gdf.boundary.plot(ax=eixo, color="black",
                             linewidth=1.3, linestyle='--')
  # Limites dos polígonos da área do projeto
  aud.boundary.plot(ax=eixo, color="#FF1493", linewidth=1.3, hatch='//')
  vege_gdf.boundary.plot(ax=eixo, color="lightgray", linewidth=0.5)
  uf_gdf.boundary.plot(ax=eixo, color="lightgray", linewidth=4)
  mun_gdf.boundary.plot(ax=eixo, color="black", linewidth=0.5)

  # Defina os limites dos eixos de plotagem
  eixo.set_ylim(miny, maxy)
  eixo.set_xlim(minx, maxx)

  # Legendas
  legend_elements = []

  area_legend = mpatches.Rectangle(
      (0, 0), 0.1, 0.1, fill=False, edgecolor="black", linewidth=1.3, linestyle='--', label='Property Area')
  legend_elements.append(area_legend)

  aud_legend = mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False, edgecolor="#FF1493",
                                  linewidth=1.3, hatch='//', label='Project Area AUD')
  legend_elements.append(aud_legend)

  uf_legend = mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False,
                                 edgecolor="lightgray", linewidth=4, label='State Boundaries')
  legend_elements.append(uf_legend)

  mun_legend = mpatches.Rectangle((0, 0), 0.1, 0.1, fill=False,
                                  edgecolor="black", linewidth=0.5, label='Municipal Boundaries')
  legend_elements.append(mun_legend)

  # Loop para plotar cada classe de vegetação utilizando as cores definidas no dicionário
  for valor in valores_unicos:
    # Selecione apenas os dados da classe sendo iterada
    data = vege_gdf[vege_gdf.legend == valor]
    # Verifique se há pelo menos um polígono da classe na área da imagem
    if data.intersects(zona_gdf.unary_union).any():
      # Use o dicionário para obter a cor correspondente
      cor = paleta.get(valor)
      # Crie um retângulo para representar a classe na legenda e adicione ao elemento da legenda
      rectangle = mpatches.Rectangle(
          (0, 0), 0.1, 0.1, facecolor=cor, edgecolor='black', label=valor)
      legend_elements.append(rectangle)
      # Plote cada classe com a cor especificada pelo dicionário
      data.plot(ax=eixo, color=cor, linewidth=1.3, label=valor)

  # Posicione a legenda à direita do mapa
  legenda = plt.legend(handles=legend_elements, bbox_to_anchor=(
      legendaX, legendaY), loc='upper left', fontsize=9)

  # Adicione rótulos aos polígonos dentro do eixo
  for x, y, label in zip(mun_gdf.geometry.centroid.x, mun_gdf.geometry.centroid.y, mun_gdf["NM_MUN"]):
    # Verifique se as coordenadas estão dentro dos limites do eixo
    if minx < x < maxx and miny < y < maxy:
      eixo.annotate(label, (x, y), xytext=(
          3, 3), textcoords="offset points", fontsize=9, ha='center', va='center')

  # Defina o estilo dos rótulos do eixo como plain para evitar que os valores sejam representados como notação científica
  eixo.ticklabel_format(style="plain")
  # Rotacione os rótulos do eixo y em 90 graus
  eixo.set_yticklabels(eixo.get_yticks(), rotation=90)
  eixo.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

  # Escala
  eixo.add_artist(ScaleBar(dx=1, location=escalaLoc))

  # Seta Norte
  eixo.annotate('N', xy=(xn, yn), xytext=(xn, yn-arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=13,
                xycoords=eixo.transAxes)

  # Carregue a imagem PNG ou JPEG
  imagem_path = './data/images/terra-vista-logo.jpg'
  imagem = plt.imread(imagem_path)

  # Crie um novo eixo para a imagem abaixo do texto Source
  imagem_eixo = fig.add_axes([x1Logo, y1Logo, x2Logo, y2Logo])

  # Plote a imagem no novo eixo
  imagem_eixo.imshow(imagem, aspect='auto')

  # Desative os eixos (ticks e labels) para o novo eixo da imagem
  imagem_eixo.set_axis_off()

  # Ajuste conforme necessário
  plt.subplots_adjust(right=0.8)

  # Adicione o texto da fonte fora da figura
  fonte = f"SIRGAS 2000 / UTM zone 19S \nSource: Vegetation Map 1:250.000 (IBGE, 2021) \nVersion: 13/12/2023 \nMunicipality/St.: {municipio}/{estado}"
  fig.text(xData, yData, fonte, va='center', fontsize=9, bbox=dict(
      boxstyle='round,pad=0.3', edgecolor='lightgray', facecolor='white'))

  return fig
