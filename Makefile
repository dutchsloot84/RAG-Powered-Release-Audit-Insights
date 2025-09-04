.PHONY: install run test lint docker-build docker-up docker-down

install:
	pip install -r requirements.txt

run:
	streamlit run app/ui/ui_app.py

test:
	pytest -q

lint:
	python -m py_compile $(git ls-files '*.py')

docker-build:
	docker build -t release-audit .

docker-up:
	docker-compose up

docker-down:
	docker-compose down
