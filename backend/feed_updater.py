import json
import os
import shutil
from zipfile import ZipFile

import requests

from backend import connection_manager, gtfs
from backend.models.feed import Feed

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

    while True:
        if 'DEBUG' in os.environ:
            response = sample_data()
        else:
            response = requests.get(transitfeed_url('/getFeeds', page=page)).json()

        if response['status'] != 'OK':
            raise ConnectionError('API responded with :' + response['status'])

        for feed_data in response['results']['feeds']:
            if 'u' in feed_data and 'd' in feed_data['u']:
                try:
                    try:
                        Feed.get(feed_id=feed_data['id'])
                    except Feed.DoesNotExist:
                        feed = Feed.create(
                            feed_id=feed_data['id'],
                            title=feed_data['t'],
                            zip_url=feed_data['u']['d'],
                            city_name=feed_data['l']['t'],
                            city_lat=feed_data['l']['lat'],
                            city_lng=feed_data['l']['lng'],
                        )

                        print(str(feed))
                except ValueError:
                    pass

        # Break from loop after processing the last page
        if page == response['results']['numPages']:
            break

        page = response['results']['page'] + 1


def update_from_feed(feed_id: str):
    try:
        feed = Feed.get(feed_id=feed_id)
    except Feed.DoesNotExist:
        raise AttributeError('Invalid feed_id: ' + feed_id)

    zip_file_name = 'temp_mvk-zrt.zip'  # download_file(feed.zip_url, feed_id)
    print('Downloaded to ' + zip_file_name)

    with ZipFile(zip_file_name, "r") as zip_ref:
        zip_ref.extractall(ZIP_EXTRACT_FOLDER)

    extracted_txt_files = [x for x in os.listdir(ZIP_EXTRACT_FOLDER) if x.endswith(".txt")]
    for file in extracted_txt_files:
        actions = {
            'agency.txt': gtfs.read_agency_txt,
            'stops.txt': gtfs.read_stops_txt,
            'routes.txt': gtfs.read_routes_txt,
            'calendar_dates.txt': gtfs.read_calendar_dates_txt,
        }

        if file in actions.keys():
            actions[file](ZIP_EXTRACT_FOLDER, feed)

            # shutil.rmtree(ZIP_EXTRACT_FOLDER)


def download_file(url, feed_id):
    local_filename = 'temp_' + feed_id[:feed_id.find('/')] + '.zip'
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename


def sample_data():
    return json.load(open('mocks/feeds.json', encoding='UTF-8'))


if __name__ == '__main__':
    connection_manager.init_db()
    # get_all_feeds()
    update_from_feed('mvk-zrt/839')
