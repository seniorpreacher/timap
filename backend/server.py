import math

from flask import Flask, render_template, json, request
from peewee import fn
from py2neo import walk, Node
from pyproj import Geod
from shapely.errors import TopologicalError
from shapely.geometry import Point, Polygon, mapping

from backend import connection_manager
from backend.connection_manager import graph
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

            g = Geod(ellps='WGS84')
            border_lat, border_lng, back_bearing = g.fwd(lat, lng, heading, radius / 2, radians=False)

            self._coords.append(Point(border_lat, border_lng))

    def get_polygon(self):
        return Polygon([[p.x, p.y] for p in self._coords])


class Intersection:
    def __init__(self, lat, lng, delay, stop_id=None):
        self.lat = lat
        self.lng = lng
        self.delay = delay
        self.stop_id = stop_id


def get_distance(lat1, lng1, lat2, lng2):
    return Geod(ellps='WGS84').inv(lng1, lat1, lng2, lat2)[2]


def get_reachable_stops(origin_stop_id, max_travel_time):
    lst = graph.run('''
        MATCH (startingPoint:Stop{id:{origin_stop_id}})
        MATCH p=(startingPoint)-[*1..10]->(endNode)
        WITH p AS shortestPath, 
             reduce(travel_time=0, r in relationships(p) | travel_time + r.travel_time) AS totalTime
        WHERE totalTime <= {max_travel_time}
        RETURN shortestPath
    ''', origin_stop_id=origin_stop_id, max_travel_time=max_travel_time)

    results = []
    __stop_set = {origin_stop_id}

    for record in lst:
        last_travel_time = 0
        for step in walk(record[0]):
            if type(step) == Node:
                previous_len = len(__stop_set)
                __stop_set.add(step['id'])

                if len(__stop_set) > previous_len:
                    results.append({
                        "stop": step,
                        "travel_time": last_travel_time
                    })
            else:
                last_travel_time += step['travel_time']

    return results


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


@app.route('/api/get-geojson')
def route_api_geojson():
    step_minutes = 15
    buffer_for_public_transport = 4  # magic, if it's more then 4 minutes it worth to wait the bus
    # steps = range(step_minutes, (4 * step_minutes) + 1, step_minutes)
    steps = [15]
    starting_point = Intersection(float(request.args.get('lat')), float(request.args.get('lng')), 0)
    intersections = [starting_point]

    # find nearby stops to the starting_point
    for minute in steps:
        for point in intersections:
            travel_with_trasport = False

            # Set if we should take public transport
            if point.stop_id is not None and step_minutes - point.delay > buffer_for_public_transport:
                travel_with_trasport = True

            # When we walk
            if not travel_with_trasport:
                nearby_stops = Stop.get_nearby(point.lat, point.lng, (minute - point.delay) * WALKING_METERS_PER_MINUTE)

                for nearby_stop in nearby_stops:
                    distance_in_minute = math.ceil(get_distance(
                        lat1=point.lat,
                        lng1=point.lng,
                        lat2=nearby_stop.lat,
                        lng2=nearby_stop.lng) / WALKING_METERS_PER_MINUTE)

                    is_new = True
                    for stored_intersection in intersections:
                        if stored_intersection.stop_id == nearby_stop.id:
                            is_new = False
                    if is_new:
                        intersections.append(
                            Intersection(nearby_stop.lat, nearby_stop.lng, distance_in_minute, nearby_stop.id)
                        )
                        print(str(nearby_stop) + ' is in ' + str(distance_in_minute) + ' min range')

            else:
                # if step_minutes - distance_in_minute > buffer_for_public_transport:
                reachable_stops = get_reachable_stops(point.stop_id, (minute - point.delay))

                for reachable_stop in reachable_stops:
                    is_new = True
                    for stored_intersection in intersections:
                        if stored_intersection.stop_id == reachable_stop['stop']['id']:
                            is_new = False
                    if is_new:
                        intersections.append(
                            Intersection(
                                lat=reachable_stop['stop']['lat'],
                                lng=reachable_stop['stop']['lng'],
                                delay=int(distance_in_minute + reachable_stop['travel_time']),
                                stop_id=reachable_stop['stop']['id']
                            )
                        )
                        print(reachable_stop['stop']['name'] + ' is in ' + str(
                            distance_in_minute + reachable_stop['travel_time']) + ' min range')

    # walking_shape = Circle(intersections[0].lng, intersections[0].lat, (steps[-1] - intersections[0].delay) * WALKING_METERS_PER_MINUTE).get_polygon()
    walking_shape = Circle(intersections[0].lng, intersections[0].lat, WALKING_METERS_PER_MINUTE).get_polygon()

    for point in intersections[1:]:
        try:
            walking_shape = walking_shape.union(
                Circle(point.lng, point.lat, (steps[-1] - point.delay) * WALKING_METERS_PER_MINUTE).get_polygon()
            )
        except TopologicalError:
            pass

    # stops = Stop.select().where(Stop.feed == Feed.get(id=main_feed_id))
    # nth_of_stop = randint(0, 20)
    # walking_shape = Point(stops[0].lng, stops[0].lat).buffer(0.01)

    # for stop in stops[1:]:
    #     walking_shape = walking_shape.union(Circle(stop.lng, stop.lat, radius).get_polygon())
    return json.dumps(mapping(walking_shape))


if __name__ == '__main__':
    connection_manager.init_db()
    app.run(
        host='0.0.0.0',
        debug=True
    )
