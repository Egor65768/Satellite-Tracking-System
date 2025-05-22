test:
	pytest tests/*.py -v

test_cov:
	pytest tests/*.py -v --cov=. --cov-report=html && google-chrome htmlcov/index.html

clean_test:
	rm -rf .coverage htmlcov

style:
	black app/ tests/