.PHONY: default dev start install

default: dev

dev:
	@dotenv venv/bin/streamlit run main.py
migrate:
	@dotenv venv/bin/python3 migrate.py
run-vegetation:
	@dotenv venv/bin/streamlit run vegetation.py
run-geomorphology:
	@dotenv venv/bin/streamlit run geomorphology.py
start:
	@streamlit run main.py
install:
	@python3 -m venv venv && venv/bin/python3 -m pip install -r requirements.txt
