import streamlit as st
import requests


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
