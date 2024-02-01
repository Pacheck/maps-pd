.PHONY: default dev start install

default: dev

dev:
	@dotenv venv/bin/streamlit run main.py
win-dev:
	@dotenv venv\Scripts\streamlit run main.py
migrate:
	@dotenv venv/bin/python migrate.py
install:
	@python -m venv venv && venv/bin/python -m pip install -r requirements.txt
win-install:
	@python -m venv venv && venv\Scripts\python -m pip install -r requirements.txt
