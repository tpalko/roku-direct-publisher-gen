#!/usr/bin/python

import os
import json
import requests
from datetime import datetime
from pytz import timezone
import subprocess
import base64
import logging

OMDBAPI_BASE = 'http://www.omdbapi.com/'
OMDBAPI_KEY = 'b361e429'
HOME_SERVER_BASE = 'http://palkosoftware.ddns.net/videos/'
VIDEO_FOLDER = '/media/storage/video/'
JSON_FEED_FILENAME = 'roku_direct_publisher_feed.json'
TZ = timezone('America/New_York')
NOW = TZ.localize(datetime.now())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
urllibLogger = logging.getLogger('urllib3')
urllibLogger.setLevel(logging.INFO)

def run():

    movies = []

    for (current_folder, dirnames, filenames) in os.walk(VIDEO_FOLDER, topdown=True):
        for filename in filenames:
            extension = filename.rpartition('.')[-1]
            if extension.lower() in ['mp4', 'm4v']:
                logger.debug("Found %s" % filename)
                base = filename.rpartition('.')[0]
                base_search = base.replace('_', '+')
                search_url = "%s?apikey=%s&t=%s" % (OMDBAPI_BASE, OMDBAPI_KEY, base_search)
                omdbapi_response = requests.get(search_url)
                omdbapi_body = omdbapi_response.json()
                if omdbapi_body['Response'] == 'True':
                    logger.info("   OMDBAPI Response %s" % filename)
                    title = omdbapi_body['Title']
                    released = datetime.strptime(omdbapi_body['Released'], "%d %b %Y") # 16 Nov 1995
                    runtime = int(omdbapi_body['Runtime'].split(' ')[0]) * 60 # 111 min
                    genres = [ g.strip().lower() for g in omdbapi_body['Genre'].split(',') ]
                    fixed_genres = []
                    for genre in genres:
                        if genre == 'animation':
                            fixed_genres.append('animated')
                        elif genre == 'musical' or genre == 'family' or genre == 'western':
                            pass
                        elif genre == 'sci-fi':
                            fixed_genres.append('science fiction')
                        else:
                            fixed_genres.append(genre)
                    plot = omdbapi_body['Plot']
                    thumbnail_filename = "%s_thumb.jpg" % base
                    if not os.path.exists(os.path.join(current_folder, thumbnail_filename)):
                        thumb_command = 'ffmpeg -i %s -ss 00:15:00.000 -vframes 1 -s 800x450 %s -hide_banner' % (os.path.join(current_folder, filename), os.path.join(current_folder, thumbnail_filename))
                        ps = subprocess.Popen(thumb_command.split(' '))
                        (out, err) = ps.communicate(None)
                    '''
                    {
                        "id": "1509428502952",
                        "title": "Pi",
                        "content": {
                          "dateAdded": "2019-03-19T05:34:03+00:00",
                          "videos": [
                            {
                              "url": "http://palkosoftware.ddns.net/videos/pi.mp4",
                              "quality": "FHD",
                              "videoType": extension.upper()
                            }
                          ],
                          "duration": 5026
                        },
                        "genres": [
                            "science fiction"
                        ],
                        "thumbnail": "http://palkosoftware.ddns.net/videos/pi_thumbnail.jpg",
                        "releaseDate": "1998-07-10",
                        "shortDescription": "A obsessed math savant brushes against the paranoid underworld of the constant Pi",
                        "tags": [
                          "recent"
                        ]
                      }
                    '''
                    folder = current_folder.replace(VIDEO_FOLDER, '')
                    url = os.path.join(HOME_SERVER_BASE, folder, filename)
                    thumbnail = os.path.join(HOME_SERVER_BASE, folder, thumbnail_filename)
                    movies.append({
                        "id": base64.encodestring(filename).strip('\n'),
                        "title": title,
                        "content": {
                          "dateAdded": datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S%z"),
                          "videos": [
                            {
                              "url": url,
                              "quality": "FHD",
                              "videoType": extension.upper()
                            }
                          ],
                          "duration": runtime
                        },
                        "genres": fixed_genres,
                        "thumbnail": thumbnail,
                        "releaseDate": datetime.strftime(released, "%Y-%m-%d"),
                        "shortDescription": plot,
                        "tags": [
                          "recent"
                        ]
                      })
    json_feed = {
        "providerName": "Palko Software Distributions",
        "lastUpdated": datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S%z"),
        "language": "en",
        "categories": [
          {
            "name": "Recently Added",
            "query": "recent",
            "order": "manual"
          }
        ],
        "movies": movies
    }

    with open(os.path.join(VIDEO_FOLDER, JSON_FEED_FILENAME), 'wb') as f:
        f.write(json.dumps(json_feed, indent=4))

if __name__ == '__main__':
    run()
