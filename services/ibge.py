import streamlit as st
import requests

BASE_URL = "https://brasilapi.com.br/api/ibge"


@st.cache_data
def get_states():
  url = f"{BASE_URL}/uf/v1"
  states = ['']

  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    for state in data:
      states.append(state['sigla'])
  else:
    print("Failed to get states")

  states.sort()
  return states


@st.cache_data
def get_cities(uf: str):
  cities = ['']

  if uf == '':
    return cities

  url = f"{BASE_URL}/municipios/v1/{uf}"
  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    for city in data:
      cities.append(city['nome'])
  else:
    print("Failed to get cities")

  return cities
