.PHONY: default dev start install

default: dev

dev:
	@dotenv venv/bin/streamlit run main.py
migrate:
	@dotenv venv/bin/python migrate.py
run-vegetation:
	@dotenv venv/bin/python vegetation.py
run-geomorphology:
	@dotenv venv/bin/python geomorphology.py
start:
	@streamlit run main.py
install:
	@python -m venv venv && venv/bin/python -m pip install -r requirements.txt
