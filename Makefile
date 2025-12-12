lint:
	flake8 .

isort:
	isort .

types:
	mypy .

test:
	pytest -q
