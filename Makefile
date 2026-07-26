SERVICE_PORT ?= 8000
IMAGE ?= llm-text-games
CONTAINER ?= llm-text-games

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run -d --name $(CONTAINER) --restart unless-stopped -p $(SERVICE_PORT):$(SERVICE_PORT) --env-file .env -e SERVICE_PORT=$(SERVICE_PORT) $(IMAGE)

docker-restart: docker-stop docker-run

docker-stop:
	-docker stop $(CONTAINER)

docker-rm:
	-docker rm -f $(CONTAINER)

docker-update: docker-stop docker-rm docker-build docker-run

web-run:
	uv run python -m app.web_server --host 0.0.0.0 --port $(SERVICE_PORT)
