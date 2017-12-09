from random import randint

import pyproj
from flask import Flask, render_template, json, request
from peewee import fn
from shapely.geometry import Point, Polygon, mapping

from backend import connection_manager
from backend.models.feed import Feed
from backend.models.stop import Stop

app = Flask(__name__)
main_feed_id = 19
WALKING_METERS_PER_MINUTE = 80


class Circle:
    # radius is in meters
    def __init__(self, lat, lng, radius, segment_count=64):
        self._coords = []
        self.center = Point(lat, lng)
        self.radius = radius

        for segment in range(segment_count):
            heading = segment * (360 / segment_count)

            g = pyproj.Geod(ellps='WGS84')
            border_lat, border_lng, back_bearing = g.fwd(lat, lng, heading, radius / 2, radians=False)

            self._coords.append(Point(border_lat, border_lng))

    def get_polygon(self):
        return Polygon([[p.x, p.y] for p in self._coords])


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
    radius = 1000
    stops = Stop.select().where(Stop.feed == Feed.get(id=main_feed_id))

    print(request.args.get('lat'), request.args.get('lng'))

    nth_of_stop = randint(0, 20)
    walking_shape = Circle(stops[nth_of_stop].lng, stops[nth_of_stop].lat, radius).get_polygon()
    # walking_shape = Point(stops[0].lng, stops[0].lat).buffer(0.01)

    # for stop in stops[1:]:
    #    walking_shape = walking_shape.union(Circle(stop.lng, stop.lat, radius).get_polygon())
    return json.dumps(mapping(walking_shape))


if __name__ == '__main__':
    connection_manager.init_db()
    app.run(
        host='0.0.0.0',
        debug=True
    )
