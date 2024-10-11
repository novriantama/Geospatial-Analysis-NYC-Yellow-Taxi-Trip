include .env

docker-build:
	@docker network inspect yellow-cab-network >/dev/null 2>&1 || docker network create yellow-cab-network
	@echo '__________________________________________________________'
	@docker build -t yellow-cab/spark -f ./docker/Dockerfile.spark .
	@echo '__________________________________________________________'
	@docker build -t yellow-cab/airflow -f ./docker/Dockerfile.airflow .
	@echo '==========================================================='

docker-compose:
	@chmod 777 logs/
	@chmod 777 scripts/entrypoint.sh
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose-spark.yml --env-file .env up -d
	@docker compose -f ./docker/docker-compose-airflow.yml --env-file .env up -d
	@echo '==========================================================='
