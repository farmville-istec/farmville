run:
	python3 api_gateway.py

test:
	python3 -m pytest tests/ -v

docker:
	docker-compose up -d