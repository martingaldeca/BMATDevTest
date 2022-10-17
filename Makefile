#!make
include .env
include .env-local
.DEFAULT_GOAL=up
MAKEFLAGS += --no-print-directory

# Constants
TAIL_LOGS = 50
PYTEST_WORKERS = 8

up: prepare-local
	$s docker compose up --force-recreate -d

down:
	$s docker compose down

down-up: down up

up-build: prepare-local
	$s docker compose down
	$s docker compose up --force-recreate -d --build

build: prepare-local
	$s docker compose build

complete-build: prepare-local
	$s docker image prune -af
	$s docker compose build
	$s docker compose down
	$s docker compose up --force-recreate -d

logs:
	$s docker logs --tail ${TAIL_LOGS} -f ${PROJECT_NAME}_backend

bash:
	$s docker exec -it ${PROJECT_NAME}_backend bash

sh:
	$s docker exec -it ${PROJECT_NAME}_backend bash

shell:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py shell_plus

shell_plus:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py shell_plus

make-migrations:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py makemigrations

migrate:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py migrate $(ARGS)

migrations:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py makemigrations
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py migrate

make-messages:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py makemessages -a

compile-messages:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py compilemessages

messages:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py makemessages -l es -a -i *.txt
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py compilemessages -v 3

worker-logs:
	$s docker exec -it ${PROJECT_NAME}_worker tail -f logs/default_worker.log

celery-logs:
	$s docker logs --tail ${TAIL_LOGS} -f ${PROJECT_NAME}_worker

beat-logs:
	$s docker logs --tail ${TAIL_LOGS} -f ${PROJECT_NAME}_beat

worker-bash:
	$s docker exec -it ${PROJECT_NAME}_worker bash

test:
	$s docker exec ${PROJECT_NAME}_backend pytest -c pytest.ini -n ${PYTEST_WORKERS} --maxfail=5 --create-db

fast-test:
	$s docker exec ${PROJECT_NAME}_backend pytest -c pytest.ini -n ${PYTEST_WORKERS} --maxfail=5 --reuse-db

local-test:
	$s docker exec ${PROJECT_NAME}_backend pytest -c pytest.ini -n ${PYTEST_WORKERS} --reuse-db

restart:
	$s docker compose restart

update-requirements:
	$s docker exec ${PROJECT_NAME}_backend poetry update

flake8:
	$s docker exec ${PROJECT_NAME}_backend flake8

all-logs:
	$s docker compose logs --tail ${TAIL_LOGS} -f

up-backend:
	$ docker compose up -d backend

prepare-local:
	$ cp ./docker/src/post_deploy.sh ./src
	$ cp ./docker/src/run* ./src

IMAGES := $(shell docker images -qa)
clean-images:
	$s docker rmi $(IMAGES) --force

CONTAINERS := $(shell docker ps -qa)
remove-containers:
	$s docker rm $(CONTAINERS)

demo-data:
	$s docker exec -it ${PROJECT_NAME}_backend python manage.py demo_data
