# Timap

## Setup

1. Get a Transitfeed API key
1. Install Postres SQL
1. Install Neo4j database engine
1. Make sure, you have Python 3.x installed
1. Setup a virtualenv: `virtaulenv venv`
1. Activate virtualenv: `./venv/bin/active` (on Unix systems)
1. Install dependencies: `pip install -r requirements.txt`

## Fill DB with data

1. Setup the following environment variables:
    - MY_PSQL_DBNAME
    - MY_PSQL_USER
    - MY_PSQL_PASSWORD
    - NEO4J_USERNAME
    - NEO4J_PASSWORD
    - TRANSITFEEDS_API_KEY
1. Run backend/feed_updater.py


## Run the server

1. Setup the same environment variables as before
1. Run backend/server.py
