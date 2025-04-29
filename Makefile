# Makefile
# Usage:
#   make up          # Start all Docker services in each directory with compose.yml
#   make down        # Stop all Docker services in each directory with compose.yml
#
#   make up DIR=minecraft   # Start Docker service *only* in directory containing "minecraft"
#   make down DIR=minecraft # Stop Docker service *only* in directory containing "minecraft"

.PHONY: up down

# Provide a DIR variable if you want to target a single matching directory
DIR ?=

up:
ifneq ($(strip $(DIR)),)
	@SINGLE_DIR=$(shell find . -type d -iname "*$(DIR)*" -print -quit); \
	if [ -z "$$SINGLE_DIR" ]; then \
		echo "No directory found matching '$(DIR)'"; \
		exit 1; \
	fi; \
	echo "==> compose.yml in: $$SINGLE_DIR"; \
	( cd "$$SINGLE_DIR" && docker compose up -d );
else
	@for f in $(shell find . -type f -name "compose.yml"); do \
		dir=$$(dirname "$$f"); \
		echo "==> compose.yml in: $$dir"; \
		( cd "$$dir" && docker compose up -d ); \
	done
endif

down:
ifneq ($(strip $(DIR)),)
	@SINGLE_DIR=$(shell find . -type d -iname "*$(DIR)*" -print -quit); \
	if [ -z "$$SINGLE_DIR" ]; then \
		echo "No directory found matching '$(DIR)'"; \
		exit 1; \
	fi; \
	echo "==> compose.yml in: $$SINGLE_DIR"; \
	( cd "$$SINGLE_DIR" && docker compose down );
else
	@for f in $(shell find . -type f -name "compose.yml"); do \
		dir=$$(dirname "$$f"); \
		echo "==> compose.yml in: $$dir"; \
		( cd "$$dir" && docker compose down ); \
	done
endif