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
OMDBAPI_KEY = os.getenv('OMDBAPI_KEY')
HOME_SERVER_BASE = os.getenv('HOME_SERVER_BASE')
VIDEO_FOLDER = os.getenv('VIDEO_FOLDER')
JSON_FEED_FILENAME = 'roku_direct_publisher_feed.json'
TZ = timezone(os.getenv('TIMEZONE'))
NOW = TZ.localize(datetime.now())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
urllibLogger = logging.getLogger('urllib3')
urllibLogger.setLevel(logging.INFO)

def run():

    movies = []
    genre_map = {
        'animation': 'animated',
        'sci-fi': 'science fiction',
        'sport': 'sports'
    }
    skip_genres = ['musical', 'family', 'western', 'short']

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
                    logger.debug("   OMDBAPI Response %s" % filename)
                    logger.debug(omdbapi_body)
                    title = omdbapi_body['Title']
                    released = datetime.strptime(omdbapi_body['Released'], "%d %b %Y") # 16 Nov 1995
                    runtime = None 
                    if omdbapi_body['Runtime'] != 'N/A':
                        runtime = int(omdbapi_body['Runtime'].split(' ')[0]) * 60 # 111 min
                    genres = [ g.strip().lower() for g in omdbapi_body['Genre'].split(',') ]                    
                    fixed_genres = [ genre_map[genre] if genre in genre_map else genre for genre in genres if genre not in skip_genres ]
                    if len(fixed_genres) == 0:
                        if title == 'Thomas & Friends: Blue Mountain Mystery':
                            fixed_genres = ['adventure', 'mystery']
                        elif title == 'Thomas & Friends: Merry Christmas, Thomas!':
                            fixed_genres = ['special']
                    plot = omdbapi_body['Plot']
                    thumbnail_filename = "%s_thumb.jpg" % base
                    if not os.path.exists(os.path.join(current_folder, thumbnail_filename)):
                        # - keyframes
                        # https://www.bugcodemaster.com/article/extract-images-frame-frame-video-file-using-ffmpeg
                        # ffmpeg -i video.webm -vf "select=eq(pict_type\,I)" -vsync vfr thumb%04d.jpg -hide_banner
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
        "providerName": os.getenv('PROVIDER_NAME'),
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
