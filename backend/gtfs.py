import csv

from backend.connection_manager import db
from backend.models.agency import Agency
from backend.models.progressbar import ProgressBar
from backend.models.route import Route
from backend.models.shape import Shape
from backend.models.stop import Stop
from backend.models.stop_time import StopTime
from backend.models.trip import Trip


def read_gtfs_file(path):
    reader = csv.DictReader(open(path, encoding='utf8'), skipinitialspace=True)
    return [dict(line) for line in reader], reader.line_num - 1


def read_agency_txt(folder, feed):
    reader = read_gtfs_file(folder + '/agency.txt')
    progress = ProgressBar(reader[1], 'agency.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
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
    progress.clear('All agencies saved', leave_bar=True)


def read_stops_txt(folder, feed):
    reader = read_gtfs_file(folder + '/stops.txt')
    progress = ProgressBar(reader[1], 'stops.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
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
    progress.clear('All stops saved', leave_bar=True)


def read_shapes_txt(folder, feed):
    reader = read_gtfs_file(folder + '/shapes.txt')
    progress = ProgressBar(reader[1], 'shapes.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
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
    progress.clear('All shapes saved', leave_bar=True)


def read_routes_txt(folder, feed):
    reader = read_gtfs_file(folder + '/routes.txt')
    progress = ProgressBar(reader[1], 'routes.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
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
    progress.clear('All routes saved', leave_bar=True)


def read_trips_txt(folder, feed):
    reader = read_gtfs_file(folder + '/trips.txt')
    progress = ProgressBar(reader[1], 'trips.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
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
    progress.clear('All trips saved', leave_bar=True)


def read_stop_times_txt(folder, feed):
    reader = read_gtfs_file(folder + '/stop_times.txt')
    progress = ProgressBar(reader[1], 'stop_times.txt')
    for line_number, data in enumerate(reader[0]):
        progress.write()
        try:
            stop = Stop.get(
                stop_id=data['stop_id'],
                feed=feed,
            )
        except Stop.DoesNotExist:
            print('not matching stop info for stop time: ' + data['stop_id'])
            continue

        try:
            trip = Trip.get(
                trip_id=data['trip_id'],
                feed=feed,
            )
        except Trip.DoesNotExist:
            print('not matching trip info for stop time: ' + data['trip_id'])
            continue

        try:
            st = StopTime.get(
                trip=trip,
                stop=stop,
            )
        except StopTime.DoesNotExist:
            st = StopTime()
            st.trip = trip
            st.stop = stop

        st.arrival_time = data['arrival_time']
        st.departure_time = data['departure_time']
        st.stop_sequence = data['stop_sequence']
        if 'stop_headsign' in data: st.stop_headsign = data['stop_headsign']
        if 'shape_dist_traveled' in data: st.shape_dist_traveled = data['shape_dist_traveled']
        st.feed = feed

        st.save()
    progress.clear('All stop times saved', leave_bar=True)


def read_calendar_dates_txt(folder, feed):
    data = read_gtfs_file(folder + '/calendar_dates.txt')
    print(data)


def connect_routes_to_stops():
    routes = Route.select()
    progress = ProgressBar(routes.count(), 'Routes «» Stops')
    for route in routes:
        progress.write(suffix=route.short_name)
        for trip in route.trips:
            for st in trip.stop_times:
                if route not in st.stop.routes:
                    st.stop.routes.add(route)
    progress.clear('Routes and Stops connected', leave_bar=True)


def simplify_stops():
    from peewee import DataError

    stops = Stop.select()
    neighbour_list = []
    progress = ProgressBar(stops.count(), 'Finding duplicates')
    for stop in stops:
        progress.write()
        try:
            cursor = db.execute_sql('''
                SELECT
                    stop.id,
                    stop.name,
                    %(distance_unit)s * DEGREES(ACOS(COS(RADIANS(%(lat)s))
                                     * COS(RADIANS(stop.lat))
                                     * COS(RADIANS(%(lng)s - stop.lng))
                                     + SIN(RADIANS(%(lat)s))
                                     * SIN(RADIANS(stop.lat)))) AS distance
                FROM stop
    
                WHERE stop.lat
                      BETWEEN %(lat)s - (%(radius)s / %(distance_unit)s)
                      AND %(lat)s + (%(radius)s / %(distance_unit)s)
                      AND stop.lng
                      BETWEEN %(lng)s - (%(radius)s / (%(distance_unit)s * COS(RADIANS(%(lat)s))))
                      AND %(lng)s + (%(radius)s / (%(distance_unit)s * COS(RADIANS(%(lat)s))))
                      AND stop.name = %(_name)s
                      AND stop.id <> %(_id)s
            ''', {
                "lat": stop.lat,
                "lng": stop.lng,
                "radius": 0.75,
                "distance_unit": 111.045,
                "_id": stop.id,
                "_name": stop.name.strip(),
            })

            all_neighbours = cursor.fetchall()
            if len(all_neighbours) > 0:
                combo = [s[0] for s in all_neighbours]
                combo.append(stop.id)
                neighbour_list.append(sorted(combo))
        except DataError:
            continue
        except Exception:
            db.rollback()
            continue

    progress.clear()

    uniquify = []
    for elem in neighbour_list:
        if elem not in uniquify:
            uniquify.append(elem)

    progress = ProgressBar(len(neighbour_list), 'Resolving duplications')

    for duplicated_stops in neighbour_list:
        stop = Stop.get(id=duplicated_stops[0])
        progress.write(suffix=stop.name)

        for duplicate_id in duplicated_stops[1:]:
            try:
                duplicate = Stop.get(id=duplicate_id)
                for st in duplicate.stop_times:
                    st.stop = stop
                    st.save()
                for sr in duplicate.routes:
                    sr.stops.remove(duplicate)
                    if stop not in sr.stops:
                        sr.stops.add(stop)
                    sr.save()
                duplicate.delete_instance()
            except Stop.DoesNotExist:
                pass

    progress.clear('All duplicates resolved')
