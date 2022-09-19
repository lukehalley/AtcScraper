# AWS #########################
newRepo:
	aws ecr create-repository --repository-name $(name) --region eu-west-1

ecr-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 538602529242.dkr.ecr.eu-west-1.amazonaws.com/atc-scraper

zeroTask:
	aws ecs update-service --cluster atc-scraperCluster --service atc-scraper --desired-count 0

oneTask:
	aws ecs update-service --cluster atc-scraperCluster --service atc-scraper --desired-count 1

createStack:
	aws cloudformation create-stack --template-body file://cloud/stack.json --stack-name atc-scraper --capabilities CAPABILITY_NAMED_IAM

updateStack:
	aws cloudformation update-stack --template-body file://cloud/stack.json --stack-name atc-scraper --capabilities CAPABILITY_NAMED_IAM

# DOCKER #########################
build:
	make -i nuke
	docker build . -t atc-scraper:$(version)
	docker run -itd atc-scraper:$(version)

logs:
	docker logs --follow $(docker ps --latest --quiet)

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