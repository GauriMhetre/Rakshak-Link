.PHONY: install seed run test build demo reset clean

install:
	pip install -r requirements.txt
	cd frontend && npm install

seed:
	python -m backend.seed

test:
	pytest backend/tests/

demo: clean seed run

reset:
	if exist rakshak_link.db del rakshak_link.db
	python -m backend.seed

run:
	python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & cd frontend && npm run dev

clean:
	if exist rakshak_link.db del rakshak_link.db
