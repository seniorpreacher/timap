import os

from playhouse.postgres_ext import PostgresqlExtDatabase
from py2neo import Graph

db = PostgresqlExtDatabase(
    os.environ.get('MY_PSQL_DBNAME'),
    user=os.environ.get('MY_PSQL_USER'),
    password=os.environ.get('MY_PSQL_PASSWORD'),
    register_hstore=False,
)

graph = Graph(
    secure=False,
    bolt=True,
    user='neo4j',
    password='password',
)


def init_db():
    db.connect()

    from backend.models.feed import Feed
    from backend.models.stop import Stop
    from backend.models.agency import Agency
    from backend.models.route import Route
    from backend.models.shape import Shape
    from backend.models.trip import Trip
    from backend.models.stop_time import StopTime
    db.create_tables([
        Feed,
        Stop,
        Route,
        Agency,
        Shape,
        Trip,
        StopTime,
        Stop.routes.get_through_model(),
    ], safe=True)
    db.close()

    print('\nDB check succeeded!\n')
