# AWS #########################
newRepo:
	aws ecr create-repository --repository-name $(name) --region eu-west-1

ecr-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper

# DOCKER #########################

exec:
	docker exec -it $(docker ps --latest --quiet) bash

tag:
	docker tag atc-scraper:$(version) 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper:$(version)

push:
	make ecr-login
	docker push 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper:$(version)

build:
	sam build

run:
	sam local invoke ATCScrape

buildAndRun:
	make build
	make run

nuke:
	docker stop $$(docker ps -a -q) & docker rm -f $$(docker ps -a -q)