clean-test-experiment-data:
	rm sp_psychopy/experiment_data/sub-a415b473_task-sp_events.tsv

start-test-experiment:
	python sp_psychopy/sp.py --sub_id a415b473
