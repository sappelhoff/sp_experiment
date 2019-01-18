clean-test-experiment-data:
	rm sp_experiment/experiment_data/sub-a415b473_task-spactive_events.tsv
	rm sp_experiment/experiment_data/sub-a415b473_task-sppassive_events.tsv

active-test-run:
	python sp_experiment/sp.py --sub_id a415b473 --condition active

passive-test-run:
	python sp_experiment/sp.py --sub_id a415b473 --condition passive
