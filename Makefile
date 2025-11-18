# Variáveis
APP := main.py

.PHONY: help
help:
	@echo ""
	@echo "Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' Makefile | sed -E 's/:.*?##/ -/'


back-dev: ## Executa FastAPI em modo dev (reload)
	@cd back && fastapi dev $(APP)

back-prd: ## Executa FastAPI em modo normal
	@cd back && fastapi run $(APP)

back-coverage: ## Roda pytest com cobertura
	@cd back && pytest --cov=. --cov-report=term-missing

back-test: ## Roda pytest com verbose nos testes/
	@cd back && pytest -v tests/

front-dev: ## executa o front end
	@cd front && ng serve --no-open --host 0.0.0.0 --port 8080

compose-up-build: ## gera a build da imagem com docker
	@cd docker && docker compose up --build

compose-up: ## roda em segundo plano
	@cd docker && docker compose up -d

compose-down: ## termina a execução
	@cd docker && docker compose down

compose-clear:
	@cd docker && \
	docker compose down || true && \
	docker container rm fastapi_back || true && \
	docker container rm fastapi_front || true && \
	docker container rm fastapi_db || true && \
	docker image rm fastapi_back_image || true && \
	docker image rm fastapi_front_image || true && \
	docker volume rm docker_fastapi_db_data || true

compose-prune:
	@cd docker && docker system prune -f && docker volume prune -f

%::
	@echo "Target inválido: '$@'"
	@$(MAKE) help
