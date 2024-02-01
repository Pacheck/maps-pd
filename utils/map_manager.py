import streamlit as st


@st.cache_data
def set_area_total_bounds(total_bounds: list[float], zoom: float):
  def get_new_min(value: float) -> float:
    return value + (min_diff / 2) - (max_diff / 2)

  def get_new_max(value: float) -> float:
    return value - (min_diff / 2) + (max_diff / 2)

  minx, miny, maxx, maxy = total_bounds

  reverse_zoom = 1 + (1 - zoom)

  minx = minx * reverse_zoom if minx > 0 else minx * zoom
  miny = miny * reverse_zoom if miny > 0 else miny * zoom
  maxx = maxx * zoom if maxx > 0 else maxx * reverse_zoom
  maxy = maxy * zoom if maxy > 0 else maxy * reverse_zoom

  x_diff = maxx - minx
  y_diff = maxy - miny
  max_diff = abs(max(x_diff, y_diff))
  min_diff = abs(min(x_diff, y_diff))

  if y_diff > x_diff:
    minx = get_new_min(minx)
    maxx = get_new_max(maxx)
  elif x_diff > y_diff:
    miny = get_new_min(miny)
    maxy = get_new_max(maxy)

  return minx, miny, maxx, maxy
