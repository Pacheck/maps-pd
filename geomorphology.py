from maps import buildGeomorphologyMap
import streamlit as st


def main():
  fig = buildGeomorphologyMap('Ipixuna', 'AM', '2')
  st.pyplot(fig)


if __name__ == '__main__':
  main()
