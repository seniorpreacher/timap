from flask import Flask, render_template, json
from peewee import fn
from shapely.geometry import *

from backend import connection_manager
from backend.models.feed import Feed
from backend.models.stop import Stop

app = Flask(__name__)
main_feed_id = 19


@app.before_request
def before_request():
    connection_manager.db.connect()


@app.after_request
def after_request(response):
    connection_manager.db.close()
    return response


@app.route('/')
def route_index():
    center_coords = Stop.select(fn.Avg(Stop.lat).alias('lat'), fn.Avg(Stop.lng).alias('lng')).get()
    return render_template('index.html', center_coords=center_coords)


"""
fn.Avg(Employee.salary)
"""


@app.route('/api/get-geojson')
def route_api_geojson():
    stops = Stop.select().where(Stop.feed == Feed.get(id=main_feed_id))
    walking_shape = Point(stops[0].lng, stops[0].lat).buffer(0.01)
    for stop in stops[1:]:
        walking_shape = walking_shape.union(Point(stop.lng, stop.lat).buffer(0.01))
    return json.dumps(mapping(walking_shape))


if __name__ == '__main__':
    connection_manager.init_db()
    app.run(
        host='0.0.0.0',
        debug=True
    )
