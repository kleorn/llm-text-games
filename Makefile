SERVICE_PORT ?= 8000

docker-build:
	docker build -t llm-text-games .

docker-run:
	docker run --rm -it --name llm-text-games --env-file .env -e SERVICE_PORT=$(SERVICE_PORT) llm-text-games

docker-restart: docker-stop docker-run

docker-stop:
	-docker stop llm-text-games

docker-rm:
	-docker rm llm-text-games

docker-update: docker-stop docker-rm docker-build docker-run
