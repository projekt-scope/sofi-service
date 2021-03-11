# Type `make` or `make help` to list available targets

# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

# The `-` in front of a command makes its exit status being ignored. Normally, a
# non-zero exit status stops the build.

# Taken from https://www.client9.com/self-documenting-makefiles/
help: ## Print this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.PHONY: help
.DEFAULT_GOAL := help

conda-create-env: ## creates a conda virtual env for this services
	conda create -n scope-env python=3.8
.PHONY: conda-create-env

install-conda: ## install requirements with conda, be sure to have the right virtual env activated
	conda install --channel conda-forge \
 	--file requirements.txt
.PHONY: install-conda

up:  ## Set-up services and start on localhost and port 8001
	uvicorn main:app --host 0.0.0.0 --port 8001

.PHONY: up

test:  ## basic test of service with example_frame
	python test_sofi.py
.PHONY: test