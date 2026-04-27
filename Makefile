VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: lint test fmt validate

lint:
	$(VENV)/bin/ruff .

fmt:
	$(VENV)/bin/black .
	$(VENV)/bin/isort .

test:
	$(PY) manage.py test

validate:
	$(PY) manage.py check
	$(PY) manage.py makemigrations --check --dry-run
	$(PY) manage.py test
	./scripts/audit-templates.py
