clean-test-experiment-data:
	rm sp_psychopy/experiment_data/sub-a415b473_task-spactive_events.tsv

start-test-experiment:
	python sp_psychopy/sp.py --sub_id a415b473 --condition active

passive-run:
	rm sp_psychopy/experiment_data/sub-a415b473_task-sppassive_events.tsv
	python sp_psychopy/sp.py --sub_id a415b473 --condition passive
