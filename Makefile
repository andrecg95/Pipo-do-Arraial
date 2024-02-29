-include .env

APP=$(PIPO_APP)
CONFIG_PATH=pyproject.toml
POETRY=poetry
PRINT=python -c "import sys; print(str(sys.argv[1]))"
DOCUMENTATION=docs
DIAGRAMS_FORMAT=plantuml

.PHONY: help
help:
	$(PRINT) "Usage:"
	$(PRINT) "    help          show this message"
	$(PRINT) "    poetry_setup  install poetry to manage python envs and workflows"
	$(PRINT) "    setup         create virtual environment and install dependencies"
	$(PRINT) "    dev_setup     create virtual environment and install dev dependencies"
	$(PRINT) "    lint          run dev utilities for code quality assurance"
	$(PRINT) "    docs          generate code documentation"
	$(PRINT) "    test          run test suite"
	$(PRINT) "    coverage      run coverage analysis"
	$(PRINT) "    set_version   set program version"
	$(PRINT) "    dist          package application for distribution"
	$(PRINT) "    image         build app docker image"
	$(PRINT) "    run_image     run app docker image in a container"
	$(PRINT) "    run_app       run docker compose"

.PHONY: poetry_setup
poetry_setup:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry config virtualenvs.in-project true

.PHONY: setup
setup:
	$(POETRY) install --all-extras --without dev

.PHONY: dev_setup
dev_setup:
	$(POETRY) install --all-extras --with docs

.PHONY: black
black:
	-$(POETRY) run black .

.PHONY: ruff
ruff:
	-$(POETRY) run ruff .

.PHONY: ruff_fix
ruff_fix:
	-$(POETRY) run ruff --fix .

.PHONY: vulture
vulture:
	-$(POETRY) run vulture

.PHONY: lint
lint: black ruff vulture

.PHONY: test
test:
	$(POETRY) run pytest --cov

.PHONY: coverage
coverage:
	$(POETRY) run coverage report -m

.PHONY: docs
docs:
	mkdir -p $(DOCUMENTATION)/_static $(DOCUMENTATION)/_diagrams
	$(POETRY) run pyreverse -p $(APP) \
		--colorized \
		-o $(DIAGRAMS_FORMAT) \
		-d $(DOCUMENTATION)/_diagrams/src $(APP)
	$(POETRY) run make -C $(DOCUMENTATION) html

.PHONY: set_version
set_version:
	$(POETRY) version $$VERSION

.PHONY: dist
dist:
	$(POETRY) dist

.PHONY: image
image: docs
	docker build . -t $(APP):latest

.PHONY: run_image
run_image: image
	docker run -d --name $(APP) --env-file .env $(APP):latest

.PHONY: run_app
run_app: docs
	docker compose up -d --build --remove-orphans
