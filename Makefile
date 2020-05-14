CONFIG_PATH=config/config.yml
OUTPUT_PATH=data/external/games.json
UPLOAD_PATH=data/external/games.json
DOWNLOAD_PATH=data/games.json
AWS_CREDENTIALS=config/aws_credentials.env

.PHONY: download_data upload_data raw_data_from_api build_docker_image

build_docker_image:
	docker build -t python_env .

raw_data_from_api: data/external/games.json config/config.yml build_docker_image

data/external/games.json: config/config.yml build_docker_image
	docker run --mount type=bind,source="`pwd`",target=/app/ python_env src/acquire.py -c=${CONFIG_PATH} -o=${OUTPUT_PATH}

upload_data: raw_data_from_api config/config.yml build_docker_image
	docker run --env-file=${AWS_CREDENTIALS} --mount type=bind,source="`pwd`",target=/app/ python_env src/upload.py -c=${CONFIG_PATH} -lfp=${UPLOAD_PATH}

download_data:
	docker run --env-file=${AWS_CREDENTIALS} --mount type=bind,source="`pwd`",target=/app/ python_env src/download.py -c=${CONFIG_PATH} -lfp=${DOWNLOAD_PATH}

ingest_data:
	source config/.mysqlconfig
	docker run --env-file=${AWS_CREDENTIALS}