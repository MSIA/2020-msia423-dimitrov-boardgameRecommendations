# MSiA423 - Analytics Value Chain - Boardgame Recommendations
## Owner: Kristiyan Dimitrov; QA: Shreyashi Ganguly

<!-- toc -->

- [JUMP TO RECREATING THE APP](#running-the-app)
- [Project Charter](#project-charter)
  * [Vision](#vision)
  * [Problem Statement](#problem-statement)
  * [Mission](#mision)
  * [Success Criteria](#success-criteria)
- [Project Backlog](#project-backlog)
- [Project Icebox](#project-icebox)
- [Directory Structure](#directory-structure)
- [Running the app in Docker](#running-the-app-in-docker)
  * [0. Make sure you're on the Northwestern VPN](#0-connect-to-northwestern-vpn)
  * [1. Build the image](#1-build-the-image)
  * [2. SQLite](#2-acquire--ingest-data-locally-sqlite)
  * [3. RDS MySQL](#3-acquire--ingest-data-to-rds)
  * [4. Raw API Data](#4-raw-api-data)
  * [5. Querying my RDS Instance](#5-querying-my-rds-instance)
  * [6. Configurations](#4-other-configurations)
  * [7. References](#5-references)

<!-- tocstop -->

## Project charter
### Vision
More people playing boardgames they love.

### Problem Statement
The number of boardgames published each year is [growing exponentially](https://medium.com/@Juliev/the-rise-of-board-games-a7074525a3ec). In 2015 alone, there were ~3,400 games published. That's almost 10 games _per day_. With such an overwhelming amount of games to choose from it can be difficult to find one you’ll like, even if you're a seasoned veteran of the boardgame world. 

### Mission
Provide a personalized boardgame recommendation system, which helps people discover games they will enjoy.

The key characteristic here is _personalized_. Currently, there are boardgame conferences, YouTube channels that review boardgames, boardgame stores, and ranking websites such as BoardGameGeek.com (“The IMDB of boardgames”). These help address the problem, but are either expensive or their opinions are subjective.

There are two relevant data sources, both of which originate from BoardGameGeek.com.
Several Kaggle datasets containing ratings, reviews, and other game information:
- [Dataset 1](https://www.kaggle.com/gabrio/board-games-dataset), [Dataset 2](https://www.kaggle.com/jvanelteren/boardgamegeek-reviews), [Dataset 3](https://www.kaggle.com/mrpantherson/board-game-data), [Dataset 4](https://www.kaggle.com/extralime/20000-boardgames-dataset)
- [Boardgamegeek XML API](https://boardgamegeek.com/wiki/page/BGG_XML_API#); [Boardgamegeek XML API 2](https://boardgamegeek.com/wiki/page/BGG_XML_API2)

### Success Criteria
- Business:
  - % positive user ratings of recommendations ("Did you like this recommendation?")
  - Click-Through-Rate to boardgamegeek.com and/or YouTube reviews (Users will be presented with links to learn more about the recommended game)
  - Avg. Time on Site and/or Avg. Number of Recommendations Requested (measured via Google Analytics)
- Statistical
  - Average RMSE of user ratings via cross-validation
  - Rank based metrics capturing relative preference: mRR, mAP, nDCG
  - % of variation explained (for Principal Components Analysis)
  - Clustering SSE (if the current categorization of games is not adequate)

## Project Backlog
<img src="figures/backlogStructure.png" alt="backlogStructure" width="170" height="110"/>

Note: Sizing for each Story is present in {brackets}
0 points - quick chore;  
1 point ~ 1 hour (small);  
2 points ~ 1/2 day (medium);  
4 points ~ 1 day (large);  
8 points - big and needs to be broken down more when it comes to execution.

__Test Hypothesis: Boardgames can be categorized based on a few key characteristics and metrics. This will help us understand the landscape better and provide more adequate recommendations.__
- Source, Ingest and clean all 4 datasets
  - Download & import datasets {1}
  - Analyze missing values & outliers {1}
  - Remove irrelevant attributes and combine datasets where relevant {2}
- Investigate Main characteristics of boardgames via Dimensionality Reduction
  - Apply & Evaluate Principal Components Analysis {4}
  - Apply & Evaluate Exploratory Factor Analysis {4}
  - Generate new features based on previous output {2}
- Investigate utility of current categorization. Is there a better, more natural segmentation of boardgames, as opposed to the current categorization?
  - Apply & Evaluate K-Means and Gaussian Mixture Clustering {2}
  - Apply & Evaluate Hierarchical clustering with different linkage methods (Average/Single/Complete) {2}

__Make recommendations/predictions for boardgames the user will like.__
- Build recommendation system
  - Random & Popular (as benchmarks) {2}
  - Content Based Filtering {8}
  - User Based & Item Based Collaborative Filtering {8}
  - Compare recommendation systems via Statistical measures of success {2}

- Investigate Predictive Model as Alternative to Recommendation system
  - Apply K-Nearest-Neighbours to show similar boardgames {4}
  - Tune hyperparameter K {1}
  - Experiment with alternative similarity measures {2}

- Compare Recommendation System results with Predictive Model results

## Project Icebox

Visualize boardgame segmentation
- Build a D3 Visualization for the clustering segmentation
- Enable export of cluster segmentation

Disclaimer: a [similar tool](https://apps.quanticfoundry.com/recommendations/tabletop/boardgame/) already exists online. Assumption is that it works via KNN.


## Directory structure

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git.
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup.
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project
│
├── test/                             <- Files necessary for running model tests (see documentation below)
│
├── app.py                            <- Flask wrapper for running the model
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies
```

## Running the app
### 0. Connect to Northwestern VPN and make sure Docker is running.

### 1. Build Docker Image
In the root directory of the project
```bash
docker build -t python_env .
```
### 2. Acquire & Ingest data locally (SQLite)

As an example, the original data files are included in the repo.
To start fresh and get up-to-date data:
```bash
make clean
```
This will delete `data/external/games.json`, `data/games.json`, and `data/boardgames.db`.

Then, to run the entire pipeline and produce a local SQLite database:

- Set your AWS credentials in `config/aws_credentials.env`.
- Specify the S3 bucket to upload to in `config/config.yml`.
- Specify the S3 bucket to download from in `config/config.yml`. In most cases, this should be the same as the upload bucket.
- Finally:

```bash
make ingest_data_sqlite
```
Expected Time to Completion: ~10 minutes.

Expected result: data/boardgames.db should be created.
What's happening?
- Data Retrieved via API and saved to `data/external/games.json`.
- Data is uploaded to S3 bucket as `games.json`.
- Data is downloaded from S3 bucket to `data/games.json`.
- SQLite database is created with table called: `boardgames`.
- Data is ingested into the SQLite database.

### 3. Acquire & Ingest data to RDS

To run the entire pipeline and produce a populated RDS database:
- If you've ran the previous step and want to test from scratch do:
```bash
make clean
```
This will delete `data/external/games.json`, `data/games.json`, and `data/boardgames.db`.

- Configure your RDS variables in `config/.mysqlconfig`. 
- Make sure the database you specify as `MYSQL_DATABASE` already exists on your RDS instance. 
- If it doesn't, create it: mysql> `CREATE DATABASE <MYSQL_DATABASE>`
- Then:
```bash
source config/.mysqlconfig
```
- Make sure you've entered your AWS credentials in `config/aws_credentials.env`.
- Make sure you've specified your S3 bucket for upload/download in `config/config.yml`
- Finally:
```bash
make ingest_data_rds
```
Expected Time to Completion: ~15 minutes, but varies b/w 10 and 20.

Expected Result: `mysql> SELECT * FROM boardgames;` should return all data (~17,311 rows)
What's happening?
- Data Retrieved via API and saved to `data/external/games.json`.
- Data is uploaded to S3 bucket as `games.json`.
- Data is downloaded from S3 bucket to `data/games.json`.
- MySQL database is created on your RDS instance with a table called: `boardgames`.
- Data is ingested into the SQLite database.

### 4. Raw API data 

The raw data from the API is included in the repo. More specifically:
- `data/game_ids.txt`: Game ids for 17,313 games from [beefsack's GitHub](https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/master/2019-07-08.csv)
- `data/raw_data.xml`: Raw XML response data as retrieved from [BoardGameGeek.com's XML API2](https://boardgamegeek.com/wiki/page/BGG_XML_API2)
- If you want to get up-to-date raw XML responses, first delete the current data by doing:
```bash
make clean_raw_data
```
This will remove `data/game_ids.txt` & `data/raw_data.xml`.  
Then, do:
```bash
make raw_xml
```
Alternatively, if you want to get raw XML data *and* upload it to your S3 bucket:
- You will need to set your S3 bucket's name in `config/config_game_ids.yml` and `config/config_raw_xml.yml`.
- Then:
```bash
make upload_raw_data
```

### 5. Querying my RDS Instance
If you want to get the boardgames data from my RDS instance then you will need to:
- Have me tell you my RDS host
- Have me create a user & password with SELECT privilages for my database
- Enter these values in `config/.mysqlconfig` and do:
```bash
source config/.mysqlconfig
```
- Finally, to establish a connection with my RDS instance, do:
```bash
docker run -it --rm mysql:latest mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
```
Expected result: You should see a `mysql>` prompt and `SHOW DATABASES` should list `msia423_first_db`.

### 6. Other Configurations

- The Makefile gives several shorthands for executing intermediate steps in each workflow (SQLite & RDS)
* `make raw_data_from_api` acquires data from API to local system
* `make upload_data` uploads data to S3 bucket specified in config/config.yml
* `make download_data` downloads data from S3 bucket specified in config/config.yml
* `make create_db_sqlite` creates `data/boardgames.db` (but doesn't ingest data).
* `make create_db_rds` creates the `boardgames` in the RDS instance specified in `config/.mysqlconfig` (but doesn't ingest data).
- You can modify the default filepaths for the `make` commands:
* `OUTPUT_PATH=<where to place data from API>`. Default: `data/external/games.json`.
* `UPLOAD_PATH=<where is the file to be uploaded to S3>`. Default: `data/external/games.json`. 
* `DOWNLOAD_PATH=<where to download the data from S3>`. Default: `data/games.json`.
* `AWS_CREDENTIALS=<where to look for AWS key & secret key`. Default: `config/aws_credentials.env`.
* `CONFIG_PATH=<where to look for config.yml>`. Default: `config/config.yml`.
- You can change the `batch_size` & `requests_per_minute` parameters of the API client. 
This, however, is not recommended, because BoardGameGeek throttles excessive requests.
The defauts (100 for both variables) should be sufficient.
- You can change the logging level in `config/logging/local.conf`. Default: `INFO`
### 7. References

- [BoardGameGeek.com's XML API2](https://boardgamegeek.com/wiki/page/BGG_XML_API2)
- [boardgamegeek2 API wrapper for the above API](https://lcosmin.github.io/boardgamegeek/modules.html)
- [beefsack's GitHub](https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/master/2019-07-08.csv)


