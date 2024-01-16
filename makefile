.PHONY: default dev start install

default: dev

dev:
	@dotenv venv/bin/streamlit run main.py
start:
	@venv/bin/streamlit run main.py
install:
	@python -m venv venv && venv/bin/python -m pip install -r requirements.txt
