.PHONY: default dev start install

default: dev

dev:
	@dotenv venv/bin/streamlit run __main__.py
start:
	@streamlit run __main__.py
install:
	@python -m venv venv && venv/bin/python -m pip install -r requirements.txt
