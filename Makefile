.PHONY: raw_data_from_api

raw_data_from_api: data/external/games.json config/config.yml

data/external/games.json: config/config.yml
	python src/acquire.py -c=config/config.yml -o=data/external/games.json