# MSiA423 - Analytics Value Chain - Boardgame Recommendations
## Owner: Kristiyan Dimitrov; QA: Shreyashi Ganguly

<!-- toc -->

- [Jump to recreating the app](#running-the-app-in-docker)
- [Project Charter](#project-charter)
  * [Vision](#vision)
  * [Problem Statement](#problem-statement)
  * [Mission](#mision)
  * [Success Criteria](#success-criteria)
- [Project Backlog](#project-backlog)
- [Project Icebox](#project-icebox)
- [Directory Structure](#directory-structure)
- [Running the app in Docker](#running-the-app-in-docker)
  * [0. Make sure you're on the Northwestern VPN](#0-make-sure-youre-on-the-northwestern-vpn)
  * [1. Build the image](#1-build-the-image)
  * [2. SQLite](#2-acquire--ingest-data-locally-sqlite)
  * [3. RDS MySQL](#3-kill-the-container)

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
### 0. Make sure you're on the Northwestern VPN

### 1. Build Docker Image
In the root directory of the project
```bash
docker build -t python_env .
```
### 2. Acquire & Ingest data locally (SQLite)

To run the entire pipeline and produce a local SQLite database:

Set your AWS credentials in config/aws_credentials.env. Then:

```bash
make create_db_sqlite
```
Expected result: data/boardgames.db should be created

#### Acquire data from BoardGameGeek.com via API

```bash
make raw_data_from_api
```
The default filepath is `data/external/games.json`. 
You can change it by specifying `make raw_data_from_api OUTPUT_PATH=<filepath>`.
IMPORTANT: If you change the path, you will have to change specify paths for subsequent steps. **Not recommended**.
NOTE: If you *insist* on changing the path, it has to be relative to src/acquire.py

The API is called via a wrapper package called [boardgamegeek2](https://lcosmin.github.io/boardgamegeek/modules.html)
You can specify the `batch_size` and `requests_per_minute` for the API client in `config/config.yml`
However, the defaults (100 for both) are recommended, because BoardGameGeek throttles excessive requests.

Finally, you can specify a different config.yml file like this: `make raw_data_from_api CONFIG_PATH=<filepath>`.
NOTE: If you do, the path has to be relative to `src/acquire.py` 

#### Upload to S3 bucket
To add an additional song:



The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database
```

### 3. Run the Flask app

To run the Flask app, run:

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker

### 1. Build the image

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo):

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.

### 2. Run the container

To run the app, run from this directory:

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port.

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container

Once finished with the app, you will need to kill the container. To do so:

```bash
docker kill test
```

where `test` is the name given in the `docker run` command.
