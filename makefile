.PHONY: black

black:
	black .

pyproject.lock: pyproject.toml
	poetry update
	poetry install ${DEV}

requirements.txt: pyproject.lock
	pip install -U poetry
	poetry show | awk '{print $$1"=="$$2}' > $@
