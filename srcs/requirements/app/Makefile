PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PYTEST ?= PYTHONPATH=. $(PYTHON) -m pytest
CONFIG ?= config/conf.yaml

.PHONY: all deps deps-dev lint format test test-all run run-ai run-no-ai clean fclean re package

all: deps-dev test

deps:
	$(PIP) install --quiet -r requirements.txt

deps-dev:
	$(PIP) install --quiet -r requirements-dev.txt

lint:
	$(PIP) install --quiet flake8
	flake8 cti_core tools tests

format:
	$(PIP) install --quiet black
	black cti_core tools tests

test:
	$(PYTEST)

test-all: test
	@echo "Full test suite completed"

run:
	$(PYTHON) main.py --config $(CONFIG)

run-ia:
	$(PYTHON) main.py --config $(CONFIG) --ai-report

run-no-ia:
	$(PYTHON) main.py --config $(CONFIG) --no-ai-report

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache build dist *.egg-info
	rm -rf data/cache.json data/cache_sites

fclean: clean
	# Artefacts de scrape et rapports
	rm -rf docs/html docs/xml docs/pdf docs/csv docs/image docs/txt
	rm -rf reports/sources reports/*.md reports_user reports
	rm -rf logs
	# Archives/dist
	rm -rf dist build

re: clean deps-dev test

package:
	mkdir -p dist
	tar --exclude='dist' --exclude='.__pycache__' --exclude='*.pyc' -czf dist/cti-scraper.tar.gz .
