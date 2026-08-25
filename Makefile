.PHONY: install test serve cycle bootstrap docker
install:
	python -m pip install -e '.[dev]'
test:
	pytest
serve:
	closure-supernet serve
cycle:
	closure-supernet cycle
bootstrap:
	closure-supernet bootstrap .
docker:
	docker compose up --build
