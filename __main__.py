import streamlit as st
from maps import buildGeomorphologyMap, buildVegetationMap
from utils import getEstados, getCidades


def main():
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

  if estado == '' or municipio == '' or mapa == '':
    st.error('Por favor, selecione um tipo de mapa, um estado e uma cidade')
    return

  fig = None
  if mapa == 'Vegetação':
    fig = buildVegetationMap(municipio, estado, project_num)
  elif mapa == 'Geomorfologia':
    fig = buildGeomorphologyMap(municipio, estado, project_num)

  st.pyplot(fig)

  print("Done!")


if __name__ == '__main__':
  main()
