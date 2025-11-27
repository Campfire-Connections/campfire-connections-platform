VENV=venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: lint test fmt

lint:
	$(VENV)/bin/ruff .

fmt:
	$(VENV)/bin/black .
	$(VENV)/bin/isort .

test:
	$(PY) manage.py test
