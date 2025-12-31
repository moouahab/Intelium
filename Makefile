APP_DIR := srcs/requirements/app
MAKE_APP := $(MAKE) -C $(APP_DIR)
COMPOSE := docker compose -f srcs/docker-compose.yml

.PHONY: help deps test build run stop logs restart clean fclean re

help:
	@echo "Targets disponibles :"
	@echo "  deps      - installe les dépendances Python dans $(APP_DIR)"
	@echo "  test      - exécute la suite de tests"
	@echo "  build     - construit les images docker"
	@echo "  run       - démarre la stack docker (scraper, métriques, mongo, vault)"
	@echo "  stop      - arrête et supprime les conteneurs"
	@echo "  logs      - suit les logs des services principaux"
	@echo "  restart   - redémarre scraper + métriques"
	@echo "  init-vault- initialise et unseal Vault (dev) puis affiche les clés"
	@echo "  clean     - nettoyage léger côté code"
	@echo "  fclean    - clean + down -v (supprime volumes)"

deps:
	$(MAKE_APP) deps

test:
	$(MAKE_APP) test

build:
	$(COMPOSE) build

run:
	$(COMPOSE) up -d --build

stop:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f cti-scraper metrics mongo vault codex prometheus grafana

restart:
	$(COMPOSE) restart cti-scraper metrics codex prometheus grafana

init-vault:
	./srcs/requirements/vault/scripts/init_vault.sh

clean:
	$(MAKE_APP) clean

fclean: clean
	$(MAKE_APP) fclean
	$(COMPOSE) down -v

re: clean deps test
