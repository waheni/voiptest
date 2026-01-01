.PHONY: help build test test-all clean install docker-build docker-test docker-shell

help:
	@echo "VoIPTest - Make targets"
	@echo ""
	@echo "Docker Commands (Recommended):"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-test     - Run tests in Docker"
	@echo "  make docker-shell    - Open shell in Docker container"
	@echo ""
	@echo "Native Commands:"
	@echo "  make install         - Install voiptest locally"
	@echo "  make test            - Run basic test"
	@echo "  make test-all        - Run all tests with JUnit output"
	@echo ""
	@echo "Lab Commands:"
	@echo "  make lab-start       - Start Asterisk lab"
	@echo "  make lab-stop        - Stop Asterisk lab"
	@echo "  make lab-logs        - View Asterisk logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Remove test results and temp files"

# Docker targets
docker-build:
	docker build -t voiptest .

docker-test:
	docker run --rm --network host -v $$(pwd):/work voiptest examples/smoke_basic.yaml

docker-test-all:
	docker run --rm --network host -v $$(pwd):/work voiptest examples/ --junit --out test-results

docker-shell:
	docker run --rm -it --network host -v $$(pwd):/work --entrypoint /bin/bash voiptest

# Native targets
install:
	pip install -e .

test:
	voiptest examples/smoke_basic.yaml

test-all:
	voiptest examples/ --junit --out test-results

# Lab targets
lab-start:
	docker-compose up -d
	@echo "Waiting for Asterisk to start..."
	@sleep 10
	@echo "Lab ready!"

lab-stop:
	docker-compose down

lab-logs:
	docker-compose logs -f asterisk

# Cleanup
clean:
	rm -rf test-results/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
