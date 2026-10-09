.PHONY: install seed run test build

install:
	pip install -r requirements.txt
	cd frontend && npm install

seed:
	python -m backend.seed

test:
	pytest

run:
	python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & cd frontend && npm run dev
