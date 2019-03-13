clean-and-reinstall:
	rm -rf .pytest_cache
	rm -rf sp_experiment/tests/__pycache__
	rm .coverage
	rm -rf sp_experiment/__pycache__
	rm -rf sp_experiment.egg-info
	pip install -e .

test:
	pytest --verbose --cov=sp_experiment
