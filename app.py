import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
from ingest import Boardgame
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask('Boardgame_Recommendations_App', static_folder='app/static' ,template_folder="app/templates")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

# Initialize the database
db = SQLAlchemy(app)

@app.route('/')
def index():
    """Main view that lists top 10 boardgames by rating in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """
    print('Executing index() function in app.route("/")')
    try:
        games = db.session.query(Boardgame).order_by(Boardgame.average_user_rating.desc()).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html', games=games)
    except:
        traceback.print_exc()
        logger.warning("Not able to display boardgames, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def show_cluster_or_id():
    """View that process a POST with new song input

    :return: redirect to index page
    """
    # If game_id is provided => find the cluster for that game and return top 10 games by user rating in that cluster
    if request.form.get('game_id'):
        try:
            cluster = db.session.query(Boardgame.cluster).filter(Boardgame.game_id == request.form['game_id']).all()
            print(f'THE RESULT OF CLUSTER IS: {cluster[0][0]}')
            cluster = cluster[0][0]
            games = db.session.query(Boardgame).filter(Boardgame.cluster == cluster).order_by(Boardgame.average_user_rating.desc()).limit(app.config["MAX_ROWS_SHOW"]).all()
            logger.debug("Returning 10 games")
            return render_template('index.html', games=games)
        except:
            traceback.print_exc()
            logger.warning("Not able to display boardgames, error page returned")
            return render_template('error.html')
    # If game_name is provided => find the cluster for the first game with a name LIKE the provided one. Return top 10 games by user rating in that cluster
    elif request.form.get('game_name'):
        try:
            search_name = f"%{request.form.get('game_name')}%"
            cluster = db.session.query(Boardgame.cluster).filter(Boardgame.name.like(search_name)).first()
            print(f'THE RESULT OF CLUSTER IS: {cluster[0]}')
            cluster = cluster[0]
            games = db.session.query(Boardgame).filter(Boardgame.cluster == cluster).order_by(Boardgame.average_user_rating.desc()).limit(app.config["MAX_ROWS_SHOW"]).all()
            logger.debug("Returning 10 games")
            return render_template('index.html', games=games)
        except:
            traceback.print_exc()
            logger.warning("Not able to display boardgames, error page returned")
            return render_template('error.html')
    # Finally, if game_cluster is provided, then return top 10 games in that cluster
    else:
        try:
            games = db.session.query(Boardgame).filter(Boardgame.cluster == request.form['cluster_id']).order_by(Boardgame.average_user_rating.desc()).limit(app.config["MAX_ROWS_SHOW"]).all()
            logger.debug("Returning 10 games")
            return render_template('index.html', games=games)
        except:
            traceback.print_exc()
            logger.warning("Not able to display boardgames, error page returned")
            return render_template('error.html')




if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])