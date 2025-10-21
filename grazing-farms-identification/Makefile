.PHONY: init run

init:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	python -m src.pipeline --config config/config.yaml
