CONFIG_PATH=config/config.yml
OUTPUT_PATH=data/external/games.json
AWS_CREDENTIALS=config/aws_credentials.env

.PHONY: upload_data raw_data_from_api build_docker_image

build_docker_image:
	docker build -t python_env .

raw_data_from_api: data/external/games.json config/config.yml build_docker_image

data/external/games.json: config/config.yml build_docker_image
	docker run --mount type=bind,source=`pwd`,target=/app/ python_env src/acquire.py -c=${CONFIG_PATH} -o=${OUTPUT_PATH}

upload_data: raw_data_from_api
	docker run --env-file=${AWS_CREDENTIALS} --mount type=bind,source=`pwd`,target=/app/ python_env src/upload.py