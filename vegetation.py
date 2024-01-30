from maps import buildVegetationMap
import streamlit as st


def main():
  fig = buildVegetationMap('Ipixuna', 'AM', '2')
  st.pyplot(fig)


if __name__ == '__main__':
  main()
