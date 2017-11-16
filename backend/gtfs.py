import csv

from backend.models.agency import Agency
from backend.models.route import Route
from backend.models.shape import Shape
from backend.models.stop import Stop
from backend.models.trip import Trip


def read_gtfs_file(path):
    return [dict(line) for line in csv.DictReader(open(path, encoding='utf8'), skipinitialspace=True)]


def read_agency_txt(folder, feed):
    for data in read_gtfs_file(folder + '/agency.txt'):
        try:
            agency = Agency.get(name=data['agency_name'])
        except Agency.DoesNotExist:
            agency = Agency()
            agency.name = data['agency_name']

        agency.agency_id = data['agency_id'] if 'agency_id' in data else None
        agency.url = data['agency_url']
        agency.timezone = data['agency_timezone']
        if 'agency_lang' in data: agency.lang = data['agency_lang']
        if 'agency_phone' in data: agency.phone = data['agency_phone']
        if 'agency_fare_url' in data: agency.fare_url = data['agency_fare_url']
        if 'agency_email' in data: agency.email = data['agency_email']
        agency.feed = feed

        agency.save()


def read_stops_txt(folder, feed):
    for data in read_gtfs_file(folder + '/stops.txt'):
        try:
            stop = Stop.get(
                stop_id=data['stop_id'],
                lat=data['stop_lat'],
                lng=data['stop_lon']
            )
        except Stop.DoesNotExist:
            stop = Stop()
            stop.stop_id = data['stop_id']
            stop.lat = data['stop_lat']
            stop.lng = data['stop_lon']

        stop.name = data['stop_name']
        if 'stop_timezone' in data: stop.timezone = data['stop_timezone']
        stop.feed = feed

        stop.save()


def read_shapes_txt(folder, feed):
    for data in read_gtfs_file(folder + '/shapes.txt'):
        try:
            shape = Shape.get(
                shape_id=data['shape_id'],
                pt_lat=data['shape_pt_lat'],
                pt_lon=data['shape_pt_lon'],
            )
        except Shape.DoesNotExist:
            shape = Shape()
            shape.shape_id = data['shape_id']
            shape.pt_lat = data['shape_pt_lat']
            shape.pt_lon = data['shape_pt_lon']

        shape.pt_sequence = data['shape_pt_sequence']
        if 'shape_dist_traveled' in data: shape.dist_traveled = data['shape_dist_traveled']
        shape.feed = feed

        shape.save()


def read_routes_txt(folder, feed):
    for data in read_gtfs_file(folder + '/routes.txt'):
        if 'route_short_name' not in data:
            data['route_short_name'] = data['route_long_name']
        if 'route_long_name' not in data:
            data['route_long_name'] = data['route_short_name']

        try:
            route = Route.get(
                route_id=data['route_id'],
                short_name=data['route_short_name'],
            )
        except Route.DoesNotExist:
            route = Route()
            route.route_id = data['route_id']
            route.short_name = data['route_short_name']

        if 'agency_id' in data:
            try:
                agency = Agency.get(
                    agency_id=data['agency_id'],
                    feed=feed
                )
                route.agency = agency

            except Agency.DoesNotExist:
                print('invalid agency id received, won\'t save for ' + route)

        route.long_name = data['route_long_name']
        route.type = data['route_type']
        if 'route_color' in data: route.route_color = data['route_color']
        if 'route_text_color' in data: route.route_text_color = data['route_text_color']
        route.feed = feed

        route.save()


def read_trips_txt(folder, feed):
    for data in read_gtfs_file(folder + '/trips.txt'):
        try:
            route = Route.get(
                route_id=data['route_id'],
                feed=feed,
            )
        except Route.DoesNotExist:
            print('not matching route info for trip: ' + data['trip_id'])
            continue

        try:
            trip = Trip.get(
                route=route,
                trip_id=data['trip_id'],
            )
        except Trip.DoesNotExist:
            trip = Trip()
            trip.route = route
            trip.trip_id = data['trip_id']

        if 'shape_id' in data:
            try:
                shape = Shape.get(
                    shape_id=data['shape_id'],
                    feed=feed
                )
                trip.shape = shape

            except Shape.DoesNotExist:
                print('invalid shape id received, won\'t save for ' + trip)

        if 'trip_short_name' in data: trip.short_name = data['trip_short_name']
        if 'trip_headsign' in data: trip.headsign = data['trip_headsign']
        if 'direction_id' in data: trip.direction = data['direction_id'] == '1'
        trip.feed = feed

        trip.save()


def read_calendar_dates_txt(folder, feed):
    data = read_gtfs_file(folder + '/calendar_dates.txt')
    print(data)
