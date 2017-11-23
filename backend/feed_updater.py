import json
import os
import shutil
from zipfile import ZipFile

import requests
from py2neo import Node, Relationship

from backend import connection_manager, gtfs
from backend.models.feed import Feed
from backend.models.progressbar import ProgressBar

ZIP_EXTRACT_FOLDER = 'zip_content'

if 'TRANSITFEEDS_API_KEY' not in os.environ:
    raise AttributeError('TRANSITFEEDS_API_KEY environment variable missing')


def transitfeed_url(path, location='undefined', page=1, limit=100):
    return 'https://api.transitfeeds.com/v1' + path + \
           '?key=' + os.environ['TRANSITFEEDS_API_KEY'] + \
           '&location=' + location + \
           '&descendants=1' \
           '&page=' + str(page) + \
           '&limit=' + str(limit) + \
           '&type=gtfs'


def get_all_feeds():
    page = 1
    progress = ProgressBar(100, prefix='Scraping feed API')

    while True:
        if 'DEBUG' in os.environ:
            response = sample_data()
        else:
            response = requests.get(transitfeed_url('/getFeeds', page=page)).json()

        if response['status'] != 'OK':
            raise ConnectionError('API responded with :' + response['status'])

        progress.total = response['results']['total']

        for feed_data in response['results']['feeds']:
            suffix = ''
            if 'u' in feed_data and 'd' in feed_data['u']:
                try:
                    try:
                        feed = Feed.get(feed_id=feed_data['id'])
                    except Feed.DoesNotExist:
                        feed = Feed()
                        feed.feed_id = feed_data['id']
                        feed.title = feed_data['t']
                        feed.zip_url = feed_data['u']['d']
                        feed.city_name = feed_data['l']['t']
                        feed.city_lat = feed_data['l']['lat']
                        feed.city_lng = feed_data['l']['lng']
                        feed.save()
                    suffix = feed.title
                except ValueError:
                    pass
            progress.write(suffix=suffix)

        # Break from loop after processing the last page
        if page == response['results']['numPages']:
            progress.clear('Feeds saved', leave_bar=True)
            break

        page = response['results']['page'] + 1


def update_from_feed(feed_id: str):
    try:
        feed = Feed.get(feed_id=feed_id)
    except Feed.DoesNotExist:
        raise AttributeError('Invalid feed_id: ' + feed_id)

    zip_file_name = download_file(feed.zip_url, feed_id)
    print('Downloaded to ' + zip_file_name)

    with ZipFile(zip_file_name, "r") as zip_ref:
        zip_ref.extractall(ZIP_EXTRACT_FOLDER)

    extracted_txt_files = [x for x in os.listdir(ZIP_EXTRACT_FOLDER) if x.endswith(".txt")]
    if 'agency.txt' in extracted_txt_files: gtfs.read_agency_txt(ZIP_EXTRACT_FOLDER, feed)
    if 'stops.txt' in extracted_txt_files: gtfs.read_stops_txt(ZIP_EXTRACT_FOLDER, feed)
    if 'shapes.txt' in extracted_txt_files: gtfs.read_shapes_txt(ZIP_EXTRACT_FOLDER, feed)
    if 'routes.txt' in extracted_txt_files: gtfs.read_routes_txt(ZIP_EXTRACT_FOLDER, feed)
    if 'trips.txt' in extracted_txt_files: gtfs.read_trips_txt(ZIP_EXTRACT_FOLDER, feed)
    if 'stop_times.txt' in extracted_txt_files: gtfs.read_stop_times_txt(ZIP_EXTRACT_FOLDER, feed)

    gtfs.connect_routes_to_stops()

    # if 'calendar_dates.txt' in extracted_txt_files: gtfs.read_calendar_dates_txt(ZIP_EXTRACT_FOLDER, feed)

    shutil.rmtree(ZIP_EXTRACT_FOLDER)


def download_file(url, feed_id):
    local_filename = 'temp_' + feed_id[:feed_id.find('/')] + '.zip'
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename


def generate_graph():
    graph = connection_manager.graph

    # clear_graph
    graph.delete_all()

    for feed in [Feed.get(feed_id='mvk-zrt/839')]: #.select():
        progress = ProgressBar(len(feed.stops), 'Stops')
        for stop in feed.stops:
            progress.write(suffix=stop.name)

            stop_node = graph.find_one('Stop', property_key='id', property_value=stop.id)
            if stop_node is None:
                stop_node = Node(
                    "Stop",
                    id=stop.id,
                    stop_id=stop.stop_id,
                    name=stop.name,
                    lat=stop.lat,
                    lng=stop.lng,
                    timezone=stop.timezone,
                )
                graph.create(stop_node)

            for route in stop.routes:
                route_node = graph.find_one('Route', property_key='id', property_value=route.id)
                if route_node is None:
                    route_node = Node(
                        "Route",
                        id=route.id,
                        route_id=route.route_id,
                        short_name=route.short_name,
                        type=route.type,
                        route_color=route.route_color,
                        route_text_color=route.route_text_color,
                    )
                    graph.create(route_node)
                graph.create(Relationship(stop_node, 'BELONGS_TO', route_node))


def sample_data():
    return json.load(open('mocks/feeds.json', encoding='UTF-8'))


if __name__ == '__main__':
    connection_manager.init_db()
    # get_all_feeds()
    update_from_feed('mvk-zrt/839')
    generate_graph()
