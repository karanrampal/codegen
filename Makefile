SHELL := /bin/bash
CONDAENV := environment.yml
REQ := requirements.txt

# Docker
PROJECT := customersegmentation-d-15ad
LOCATION := europe-west1
REGISTRY := codegen
VERSION := latest
IMG := analytical-assistant:$(VERSION)

install: $(CONDAENV)
	conda env create -f $(CONDAENV)

install_ci: $(REQ)
	pip install --upgrade pip &&\
		pip install -r $(REQ)

build:
	python -m build

test:
	pytest -vv --cov --disable-warnings --cov-report=xml

format:
	black src tests
	isort src tests
	mypy src tests

lint:
	pylint -j 4 src tests/*

docker_bp: Dockerfile
	docker build -f Dockerfile -t $(LOCATION)-docker.pkg.dev/$(PROJECT)/$(REGISTRY)/$(IMG) ./
	docker push $(LOCATION)-docker.pkg.dev/$(PROJECT)/$(REGISTRY)/$(IMG)

clean:
	find . \( -name "coverage.xml" -o -name ".coverage" \) -exec rm {} +
	find . \( -name "__pycache__" -o -name ".ipynb_checkpoints" -o -name ".mypy_cache" -o -name ".pytest_cache" -o -name "dist" \) -exec rm -r {} +
	find ./src -name "*.egg-info" -exec rm -r {} +

all: install lint test

.PHONY: lint format clean all