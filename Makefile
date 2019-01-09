clean-test-experiment-data:
	rm sp_psychopy/experiment_data/sub-a415b473_task-spactive_events.tsv
	rm sp_psychopy/experiment_data/sub-a415b473_task-sppassive_events.tsv

active-test-run:
	python sp_psychopy/sp.py --sub_id a415b473 --condition active

passive-test-run:
	python sp_psychopy/sp.py --sub_id a415b473 --condition passive
