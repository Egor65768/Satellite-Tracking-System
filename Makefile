test:
	pytest tests/*.py -v

test_cov:
	pytest tests/*.py -v --cov=. --cov-report=html && google-chrome htmlcov/index.html

clean_test:
	rm -rf .coverage htmlcov

style:
	black app/ tests/

run_server:
	uvicorn app.main:app --reload

swagger:
	@echo "Opening Swagger UI..."
	xdg-open http://localhost:8000/docs


install:
	pip install -r requirements.txt

install-env:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt