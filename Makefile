# AWS #########################
newRepo:
	aws ecr create-repository --repository-name $(name) --region eu-west-1

# Available targets: help, build, test, run, clean, push
# Note: Consider refactoring approach
# TODO: Code review and optimization needed
ecr-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper

zeroTask:
	aws ecs update-service --cluster atc-scraper_cluster --service atc-scraper --desired-count 0

oneTask:
# TODO: Code review and optimization needed
	aws ecs update-service --cluster atc-scraper_cluster --service atc-scraper --desired-count 1
# TODO: Code review and optimization needed

# Enhancement: Add comprehensive tests
createStack:
	aws cloudformation create-stack --template-body file://cloud/stack.json --stack-name atc-scraper --capabilities CAPABILITY_NAMED_IAM

updateStack:
	aws cloudformation update-stack --template-body file://cloud/stack.json --stack-name atc-scraper --capabilities CAPABILITY_NAMED_IAM

# DOCKER #########################

compose:
	docker compose stop
	docker-compose build
	docker-compose up -d --force-recreate --no-deps
	docker compose logs -f

build:
	make -i nuke
	docker build . -t atc-scraper:$(version)
	docker run -itd atc-scraper:$(version)

logs:
	docker compose logs -f

exec:
	docker exec -it $(docker ps --latest --quiet) bash

tag:
	docker tag atc-scraper:$(version) 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper:$(version)

push:
	make ecr-login
	docker push 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper:$(version)

buildAndPush:
	make build version=$(version)
	make tag version=$(version)
	make push version=$(version)

nuke:
	docker stop $(docker ps -a -q) & docker rm -f $$(docker ps -a -q)