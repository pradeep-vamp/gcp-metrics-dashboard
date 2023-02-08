# makefile simplifies running local quality checks while developing.
MAKEFLAGS		= --no-print-directory --no-builtin-rules
# Signifies our desired python version
# Makefile macros (or variables) are defined a little bit differently than traditional bash, keep in mind that in the Makefile there's top-level Makefile-only syntax, and everything else is bash script syntax.
# If virtualenv exists, use it. If not, use PATH to find
SYSTEM_PYTHON	= $(or $(shell which python3), $(shell which python))
PYTHON			= $(or $(wildcard 	), $(SYSTEM_PYTHON))

# Defines the default target that `make` will to try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = help

# The @ makes sure that the command itself isn't echoed in the terminal
help:
	@echo "---------------HELP-----------------"
	@echo "To execute commands run 'make CMD' which is mentioned below"
	@echo "venv: copies the .env-example to .env under each project folder"
	@echo "env: copies the .envrc-sample to .env under each project folder"
	@echo "install: installs packages needed for dev"
	@echo "test: the project type make test which runs the tests on all projects"
	@echo "build: the project type make build"
	@echo "run: the project type make run"
	@echo "lint: does linting on the entire project"
	@echo "format: does code import sort and code formating using black"
	@echo "precommit: runs the precommit task done before commiting a branch"
	@echo "ci: runs the CI/CD task done before commiting a branch"
	@echo "upgrade-dev: runs pip-upgrade on the requirment-dev.txt file for local install and devlopment"
	@echo "upgrade-prod: runs pip-upgrade on the requirment.txt file for production release"
	@echo "upgrade: runs pip-upgrade on all the requirment files packages"
	@echo "------------------------------------"

venv:
	$(SYSTEM_PYTHON) -m pip install virtualenv virtualenvwrapper
	rm -rf env
	$(SYSTEM_PYTHON) -m venv env
	${SYSTEM_PYTHON} -m virtualenv env --python=python3.8
	PYTHONPATH=env; . ./env/bin/activate
	which ${PYTHON}

install:
	brew install git-secrets
	${PYTHON} -m pip install --upgrade pip setuptools wheel pip-upgrader
	${PYTHON} -m pip install awsebcli --upgrade
	${PYTHON} -m pip install -r requirements-dev.txt
	pre-commit install

lint:
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports --verbose --recursive *.py

login:
	@echo "No login process in this project"
	@echo "Happy Days!!!"

build:
	docker build . -t metrics

test:
	${PYTHON} run_tests.py

cpenv:
	cp .envrc.sample .envrc
	cp .env-example .env

run:
	@echo "Manually run the following cmd in terminal directly 'docker run -it -v $PWD:/app -p 8080:8080 --env-file=.env metrics'"

upgrade-dev:
	pip-upgrade requirements-dev.txt

upgrade-prod:
	pip-upgrade requirements.txt

upgrade: upgrade-dev upgrade-prod

freeze-dev:
	${PYTHON} -m pip freeze > requirements-dev.txt

freeze-prod:
	${PYTHON} -m pip freeze > requirements.txt

freeze: freeze-dev freeze-prod

format:
	${PYTHON} -m isort . --profile=black --filter-files
	${PYTHON} -m black .

precommit:
	pre-commit run

ci: precommit clean format lint test

clean:
	rm -rf __pycache__
	rm -rf env

# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = help format clean ci test lint login cpenv build run precommit install venv upgrade upgrade-prod upgrade-dev freeze freeze-dev freeze-prod
