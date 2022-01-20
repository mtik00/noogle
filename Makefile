.PHONY: build push

build:
	docker build -t mtik00/noogle:latest --pull .

push:
	docker push mtik00/noogle:latest
