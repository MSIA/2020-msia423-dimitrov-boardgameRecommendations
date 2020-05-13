CONFIG_PATH=config/config.yml
OUTPUT_PATH=data/external/games.json

.PHONY: raw_data_from_api

raw_data_from_api: data/external/games.json config/config.yml

data/external/games.json: config/config.yml
	python src/acquire.py -c=${CONFIG_PATH} -o=${OUTPUT_PATH}