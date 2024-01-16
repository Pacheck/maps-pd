import geopandas as gpd
import pandas as pd
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.wkt import loads
import streamlit as st
import requests
from google.cloud import bigquery
import asyncio

client = bigquery.Client(project='moss-forest')


async def asyncQueryToGDF(query: str) -> gpd.GeoDataFrame:
  loop = asyncio.get_event_loop()
  query_job = await loop.run_in_executor(None, client.query, query)
  df = await loop.run_in_executor(None, query_job.to_dataframe)
  df['geometry'] = df['geometry'].apply(loads)
  gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
  gdf = gdf.to_crs(crs='EPSG:31979')
  return gdf


async def loadData(estado: str, project_num: str):
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
  ]

  tasks = (asyncQueryToGDF(query) for query in queries)

  gdfs = await asyncio.gather(*tasks)

  return gdfs


async def loadVegetationData():
  # Vegetação IBGE para o município de interesse
  query = f"""
  SELECT * FROM `moss-forest.pd_forest.IBGE_vegetacao` a
  JOIN `moss-forest.limites_projetos.seringueira_buffer_200km` b
  ON ST_INTERSECTS((ST_GEOGFROMTEXT(a.geometry, make_valid => True)), (ST_GEOGFROMTEXT(b.geometry, make_valid => True)))
  WHERE ST_INTERSECTION(ST_GEOGFROMTEXT(a.geometry, make_valid => True), (ST_GEOGFROMTEXT(b.geometry, make_valid => True))) IS NOT NULL
  """
  vege_gdf = await asyncQueryToGDF(query)

  return vege_gdf


async def loadGeomorphologyData():
  # Dados de Geomorfologia
  query = """
          SELECT * FROM `moss-forest.pd_forest.IBGE_geomorfologia` a
          JOIN `moss-forest.limites_projetos.seringueira_buffer_200km` b
          ON ST_INTERSECTS((ST_GEOGFROMTEXT(a.geometry, make_valid => True)), (ST_GEOGFROMTEXT(b.geometry, make_valid => True)))
          WHERE ST_INTERSECTION(ST_GEOGFROMTEXT(a.geometry, make_valid => True), (ST_GEOGFROMTEXT(b.geometry, make_valid => True))) IS NOT NULL
          """

  geomorf_gdf = await asyncQueryToGDF(query)

  return geomorf_gdf


@st.cache_data
def getEstados():
  url = "https://brasilapi.com.br/api/ibge/uf/v1"
  estados = ['']

  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    for estado in data:
      estados.append(estado['sigla'])
  else:
    print("Failed to get states")

  estados.sort()

  return estados


@st.cache_data
def getCidades(uf):
  cidades = ['']

  if uf == '':
    return cidades

  url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{uf}"
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    for cidade in data:
      cidades.append(cidade['nome'])
  else:
    print("Failed to get cities")

  return cidades


async def main():
  st.sidebar.title('Configurações')

  project_num = st.sidebar.selectbox('Selecione o n° do projeto', ['2'])

  mapas = ['Vegetação', 'Geomorfologia']
  mapa = st.sidebar.selectbox('Selecione o tipo de mapa', mapas)

  if mapa != '':
    st.title(f'Mapa de {mapa}')

  estados = getEstados()
  estado = st.sidebar.selectbox('Selecione o Estado', estados)

  cidades = getCidades(estado)
  municipio = st.sidebar.selectbox('Selecione a cidade', cidades)

  # Dicionário que vai definir as cores de plotagem de cada classe de vegetação
  paleta = {}
  paleta2 = {}
  paleta3 = {}

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

  paleta_geom_default_colors = [
      ('Phanerozoic Sedimentary Basins and Cover', '#9ACD32'),
      ('Quaternary Sedimentary Deposits', '#FFFACD'),
      ('Continental Water Body', '#0000ff')
  ]

  paleta_geom2_default_colors = [
      ('Cruzeiro do Sul Tabular Surface', '#2E8B57'),
      ('Marginal Depression at Serra do Divisor', '#808000'),
      ('Serra do Divisor Residual Plateaus', '#00FA9A'),
      ('Javari Depression -- Juruá', '#00FF00'),
      ('Juruá Depression -- Iaco', '#228B22'),
      ('Continental Water Body ', '#0000ff'),
      ('Amazon Plain', '#FFFACD')
  ]

  paleta_geom3_default_colors = [
      ('tabular top', '#F4A460'),
      ('sharp top', '#FFD700'),
      ('convex top', '#D8BFD8'),
      ('steep erosion slope', '#FA8072'),
      ('pediplain', '#E9967A'),
      ('terrace', '#9ACD32'),
      ('plain', '#FFFACD'),
      ('eroded plain', '#DB7093'),
      ('plain and terrace', '#228B22')
  ]

  if mapa == 'Vegetação':
    with st.sidebar.expander("Paleta de cores"):
      for key, color in paleta_vege_default_colors:
        paleta[key] = st.color_picker(key, color)

  elif mapa == 'Geomorfologia':
    with st.sidebar.expander("Paleta de cores 1"):
      for key, color in paleta_geom_default_colors:
        paleta[key] = st.color_picker(key, color)
    with st.sidebar.expander("Paleta de cores 2"):
      for key, color in paleta_geom2_default_colors:
        paleta2[key] = st.color_picker(key, color)
    with st.sidebar.expander("Paleta de cores 3"):
      for key, color in paleta_geom3_default_colors:
        paleta3[key] = st.color_picker(key, color)

  if estado == '' or municipio == '' or mapa == '':
    st.error('Por favor, selecione um tipo de mapa, um estado e uma cidade')
    return

  uf_gdf, mun_gdf, areaproj_gdf, aud, zoom_gdf, zona_gdf = await loadData(
      estado, project_num)

  fig = None
  if mapa == 'Vegetação':
    vege_gdf = await loadVegetationData()

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

    # map_vege = './data/images/Vegetacao.png'
    # fig.savefig(map_vege, bbox_inches='tight', dpi=300)

  elif mapa == 'Geomorfologia':
    geomorf_gdf = await loadGeomorphologyData()

    dominios = geomorf_gdf['nm_dominio_legend'].unique()

    geomorf_gdf_fil = geomorf_gdf[geomorf_gdf['nm_unidade_legend'].notna()]
    geomorf_gdf_fil2 = geomorf_gdf[geomorf_gdf['forma_legend'].notna()]

    # Figure Geomorphology of the region where the Seringueira project is located
    import matplotlib.gridspec as gridspec
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    fig = plt.figure(figsize=(12, 12))

    gs = gridspec.GridSpec(3, 1)

    plot1 = plt.subplot(gs[0, 0])
    plot2 = plt.subplot(gs[1, 0])
    plot3 = plt.subplot(gs[2, 0])

    plot1.set_xticks([])
    plot1.set_yticks([])

    plot2.set_xticks([])
    plot2.set_yticks([])

    plot3.set_xticks([])
    plot3.set_yticks([])

    minx, miny, maxx, maxy = zoom_gdf.total_bounds
    # Limites dos polígonos da área do projeto
    areaproj_gdf.boundary.plot(ax=plot1, color="black", linewidth=1.3)
    # Limites dos polígonos da área do projeto
    aud.boundary.plot(ax=plot1, color="#FF1493", linewidth=1.3, hatch='//')
    uf_gdf.boundary.plot(ax=plot1, color="lightgray", linewidth=4)
    mun_gdf.boundary.plot(ax=plot1, color="black", linewidth=0.5)

    # Defina os limites dos eixos de plotagem
    plot1.set_ylim(miny, maxy)
    plot1.set_xlim(minx, maxx)

    # Legendas
    legend_elements = []

    area_legend = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="black", linewidth=1.3, label='Property Area')
    legend_elements.append(area_legend)

    aud_legend = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="#FF1493", linewidth=1.3, hatch='//', label='Project Area AUD')
    legend_elements.append(aud_legend)

    uf_legend = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="lightgray", linewidth=4, label='State Boundaries')
    legend_elements.append(uf_legend)

    mun_legend = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="black", linewidth=0.5, label='Municipal Boundaries')
    legend_elements.append(mun_legend)

    import_legend1 = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="white", linewidth=1.3, label='Morphostructural Domains')
    legend_elements.append(import_legend1)

    # Criar uma legenda
    gridcode_legend_elements = []

    # Criar uma legenda
    gridcode_legend_elements = []
    # Loop para plotar cada classe utilizando as cores definidas no dicionário
    for valor in dominios:
        # Selecione apenas os dados da classe sendo iterada
      data = geomorf_gdf[geomorf_gdf.nm_dominio_legend == valor]
      # Use o o dicionário para obter a cor correspondente
      cor = paleta.get(valor)
      label = f'{valor}'
      # Crie um retângulo para representar a classe na legenda e adicione ao elemento da legenda
      rectangle = mpatches.Rectangle(
          (0, 0), 1, 1, facecolor=cor, edgecolor='black', label=f'{label}')
      gridcode_legend_elements.append(rectangle)
      # Plote cada classe com a cor especificada pelo dicionário
      data.plot(ax=plot1, color=cor, linewidth=1.3, label=valor)

    legend_elements.extend(gridcode_legend_elements)

    # Defina o estilo dos rótulos do eixo como plain para evitar que os valores sejam representados como notação científica
    plot1.ticklabel_format(style="plain")
    # Rotacione os rótulos do eixo y em 90 graus
    plot1.set_yticklabels(plot1.get_yticks(), rotation=90)
    plot1.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

    # Seta Norte
    xn, yn, arrow_length = 0.91, 0.2, 0.08
    plot1.annotate('N', xy=(xn, yn), xytext=(xn, yn-arrow_length),
                   arrowprops=dict(facecolor='black', width=5, headwidth=15),
                   ha='center', va='center', fontsize=13,
                   xycoords=plot3.transAxes)

    # Escala
    plot1.add_artist(ScaleBar(dx=1, location="lower right"))

    # PLOT 2

    minx, miny, maxx, maxy = zoom_gdf.total_bounds
    # Limites dos polígonos da área do projeto
    areaproj_gdf.boundary.plot(ax=plot2, color="black", linewidth=1.3)
    # Limites dos polígonos da área do projeto
    aud.boundary.plot(ax=plot2, color="#FF1493", linewidth=1.3, hatch='//')
    uf_gdf.boundary.plot(ax=plot2, color="lightgray", linewidth=4)
    mun_gdf.boundary.plot(ax=plot2, color="black", linewidth=0.5)

    # Defina os limites dos eixos de plotagem
    plot2.set_ylim(miny, maxy)
    plot2.set_xlim(minx, maxx)

    import_legend2 = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="white", linewidth=1.3, label='Geomorphological Units')
    legend_elements.append(import_legend2)

    # Criar uma legenda
    gridcode_legend_elements2 = []

    # Criar uma legenda
    gridcode_legend_elements2 = []
    # Loop para plotar cada classe utilizando as cores definidas no dicionário
    for valor in paleta2:
      # Selecione apenas os dados da classe sendo iterada
      data = geomorf_gdf_fil[geomorf_gdf_fil.nm_unidade_legend == valor]
      # Use o o dicionário para obter a cor correspondente
      cor = paleta2.get(valor)
      label = f'{valor}'
      # Crie um retângulo para representar a classe na legenda e adicione ao elemento da legenda
      rectangle = mpatches.Rectangle(
          (0, 0), 1, 1, facecolor=cor, edgecolor='black', label=f'{label}')
      gridcode_legend_elements2.append(rectangle)
      # Plote cada classe com a cor especificada pelo dicionário
      data.plot(ax=plot2, color=cor, linewidth=1.3, label=valor)

    legend_elements.extend(gridcode_legend_elements2)

    # Defina o estilo dos rótulos do eixo como plain para evitar que os valores sejam representados como notação científica
    plot2.ticklabel_format(style="plain")
    # Rotacione os rótulos do eixo y em 90 graus
    plot2.set_yticklabels(plot2.get_yticks(), rotation=90)
    plot2.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

    # Escala
    plot2.add_artist(ScaleBar(dx=1, location="lower right"))

    # PLOT 3

    minx, miny, maxx, maxy = zoom_gdf.total_bounds
    # Limites dos polígonos da área do projeto
    areaproj_gdf.boundary.plot(ax=plot3, color="black", linewidth=1.3)
    # Limites dos polígonos da área do projeto
    aud.boundary.plot(ax=plot3, color="#FF1493", linewidth=1.3, hatch='//')
    uf_gdf.boundary.plot(ax=plot3, color="lightgray", linewidth=4)
    mun_gdf.boundary.plot(ax=plot3, color="black", linewidth=0.5)

    # Defina os limites dos eixos de plotagem
    plot3.set_ylim(miny, maxy)
    plot3.set_xlim(minx, maxx)

    import_legend3 = mpatches.Rectangle(
        (0, 0), 0.1, 0.1, fill=False, edgecolor="white", linewidth=1.3, label='Form of the Modeling')
    legend_elements.append(import_legend3)

    # Criar uma legenda
    gridcode_legend_elements3 = []

    # Criar uma legenda
    gridcode_legend_elements3 = []
    # Loop para plotar cada classe utilizando as cores definidas no dicionário
    for valor in paleta3:
      # Selecione apenas os dados da classe sendo iterada
      data = geomorf_gdf_fil2[geomorf_gdf_fil2.forma_legend == valor]
      # Use o o dicionário para obter a cor correspondente
      cor = paleta3.get(valor)
      label = f'{valor}'
      # Crie um retângulo para representar a classe na legenda e adicione ao elemento da legenda
      rectangle = mpatches.Rectangle(
          (0, 0), 1, 1, facecolor=cor, edgecolor='black', label=f'{label}')
      gridcode_legend_elements3.append(rectangle)
      # Plote cada classe com a cor especificada pelo dicionário
      data.plot(ax=plot3, color=cor, linewidth=1.3, label=valor)

    legend_elements.extend(gridcode_legend_elements3)

    # Defina o estilo dos rótulos do eixo como plain para evitar que os valores sejam representados como notação científica
    plot3.ticklabel_format(style="plain")
    # Rotacione os rótulos do eixo y em 90 graus
    plot3.set_yticklabels(plot3.get_yticks(), rotation=90)
    plot3.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

    # Escala
    plot3.add_artist(ScaleBar(dx=1, location="lower right"))

    legenda = plt.legend(handles=legend_elements, bbox_to_anchor=(
        1.05, 3.42), loc='upper left', fontsize=9)

    for text in legenda.get_texts():
      if text.get_text() in ['Morphostructural Domains', 'Geomorphological Units', 'Form of the Modeling']:
        text.set_fontweight('bold')

    # Carregue a imagem PNG ou JPEG
    imagem_path = './data/images/terra-vista-logo.jpg'
    imagem = plt.imread(imagem_path)

    # Crie um novo eixo para a imagem abaixo do texto Source
    imagem_eixo = fig.add_axes([0.6, 0.13, 0.23, 0.04])

    # Plote a imagem no novo eixo
    imagem_eixo.imshow(imagem, aspect='auto')

    # Desative os eixos (ticks e labels) para o novo eixo da imagem
    imagem_eixo.set_axis_off()

    # Ajuste conforme necessário
    plt.subplots_adjust(right=0.8)

    # Adicione o texto da fonte fora da figura
    fonte = "SIRGAS 2000 / UTM zone 19S \nSource: Geomorphology Map - 1:250.000 (IBGE, 2023) \nVersion: 13/12/2023 \nMunicipality/St.: Ipixuna/AM"
    fig.text(0.6, 0.21, fonte, va='center', fontsize=9, bbox=dict(
        boxstyle='round,pad=0.3', edgecolor='lightgray', facecolor='white'))

    # map_geom = './data/images/Geomorfologia.png'
    # fig.savefig(map_geom, bbox_inches='tight', dpi=300)

  if fig == None:
    st.error('Erro ao carregar o mapa')
    return

  st.pyplot(fig)

  print("Done!")


asyncio.run(main())
