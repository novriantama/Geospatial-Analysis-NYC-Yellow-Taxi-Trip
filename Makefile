include .env

docker-build:
	@docker network inspect yellow-cab-network >/dev/null 2>&1 || docker network create yellow-cab-network
	@echo '__________________________________________________________'
	@docker build -t yellow-cab/duckdb -f ./docker/Dockerfile.duckdb .
	@echo '__________________________________________________________'
	@docker build -t yellow-cab/airflow -f ./docker/Dockerfile.airflow .
	@echo '==========================================================='

docker-compose:
	@chmod 777 scripts/entrypoint-airflow.sh
	@echo '__________________________________________________________'
	@docker compose -f ./docker/docker-compose.yml --env-file .env up -d
	@echo '==========================================================='
