.PHONY: run test docker clean

run:
	python3 api_gateway.py

test:
	python3 -m pytest tests/ -v

docker:
	docker-compose up -d

runService:
	python api_gateway.py

runTest:
	python -m pytest tests/

docs-build:
	python build_docs.py build

docs-open:
	python build_docs.py open

docs: docs-build docs-open

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
