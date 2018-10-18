.PHONY: black

black:
	black .

poetry.lock: pyproject.toml
	poetry lock

requirements.txt: poetry.lock
	pip install -U poetry
	poetry install ${DEV}
	poetry show | awk '{print $$1"=="$$2}' > $@
