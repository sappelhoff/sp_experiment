help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  clean         to clean and reinstall"
	@echo "  test          to run the test suite"
	@echo "  run           to start the experiment navigation"

clean:
	rm -rf .pytest_cache
	rm -rf sp_experiment/tests/__pycache__
	rm .coverage
	rm -rf sp_experiment/__pycache__
	rm -rf sp_experiment.egg-info
	pip install -e .

run:
	python sp_experiment/sp.py

test:
	pytest --verbose --cov=sp_experiment
	flake8 .
