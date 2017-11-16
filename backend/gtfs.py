import csv

from backend.models.agency import Agency
from backend.models.route import Route
from backend.models.stop import Stop


def read_gtfs_file(path):
    return [dict(line) for line in csv.DictReader(open(path, encoding='utf8'), skipinitialspace=True)]


def read_agency_txt(folder, feed):
    for data in read_gtfs_file(folder + '/agency.txt'):
        try:
            agency = Agency.get(name=data['agency_name'])
        except Agency.DoesNotExist:
            agency = Agency()

        agency.agency_id = data['agency_id'] if 'agency_id' in data else None
        agency.name = data['agency_name']
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
        stop.name = data['stop_name']
        stop.lat = data['stop_lat']
        stop.lng = data['stop_lon']
        if 'stop_timezone' in data: stop.timezone = data['stop_timezone']
        stop.feed = feed

        stop.save()


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

        if 'agency_id' in data:
            try:
                agency = Agency.get(
                    agency_id=data['agency_id'],
                    feed=feed
                )
                route.agency = agency

            except Agency.DoesNotExist:
                print('invalid agency id received, won\'t save')

        route.route_id = data['route_id']
        route.short_name = data['route_short_name']
        route.long_name = data['route_long_name']
        route.type = data['route_type']
        if 'route_color' in data: route.route_color = data['route_color']
        if 'route_text_color' in data: route.route_text_color = data['route_text_color']
        route.feed = feed

        route.save()


def read_calendar_dates_txt(folder, feed):
    data = read_gtfs_file(folder + '/calendar_dates.txt')
    print(data)
