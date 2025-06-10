.PHONY: run test docker clean

run:
	python3 api_gateway.py

test:
	python3 -m pytest tests/ -v

docker:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
