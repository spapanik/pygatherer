.PHONY: black

black:
	black .

pyproject.lock: pyproject.toml
	pip install -U poetry
	poetry install ${DEV}

requirements.txt: pyproject.lock
	poetry show | awk '{print $$1"=="$$2}' > $@
