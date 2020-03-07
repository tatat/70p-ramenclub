import os
from storage import Storage
from utils import kml_simplify, kml_diff
import requests
from requests_oauthlib import OAuth1Session
import shutil
import tempfile
from tenacity import retry, stop_after_attempt, wait_random
import json


def render(data):
    lng, lat, *_ = data['coordinates'].split(',')

    extra_data = {
        'lat': lat,
        'lng': lng
    }

    return """
{name}
{lat},{lng}

https://www.google.com/maps/d/viewer?mid=1L6R9EqLu2YM3J-_ojg08ySgdcKboPwye&ll={lat}%2C{lng}&z=14
    """.format(**{ **data, **extra_data })


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_random(min=1, max=3))
def run_task(data, oauth):
    media_ids = []

    for media in data['media']:
        response = requests.get(media, stream=True)

        if response.status_code != 200:
            raise Exception('status_code={}, response={}'.format(response.status_code, response.text))

        with tempfile.TemporaryFile() as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

            f.seek(0)
            response = oauth.post('https://upload.twitter.com/1.1/media/upload.json', files={ 'media': f })

            if response.status_code == 200:
                print('Uploaded Media: {}'.format(response.text))

                media_ids.append(json.loads(response.text).get('media_id_string'))
            else:
                raise Exception('status_code={}, response={}'.format(response.status_code, response.text))

    params = { 'status': render(data) }

    if len(media_ids) > 0:
        params['media_ids'] = ','.join(media_ids)

    response = oauth.post('https://api.twitter.com/1.1/statuses/update.json', data=params)

    if response.status_code != 200:
        raise Exception('status_code={}, response={}'.format(response.status_code, response.text))
    else:
        print('Posted: {}'.format(response.text))


def lambda_handler(event, context):
    storage = Storage('current', default_value=[])
    response = requests.get(os.environ['KML_URL'])

    if response.status_code != 200:
        raise Exception('Failed to get KML')

    data = kml_simplify(response.text)
    last_data = storage.read()
    diff = kml_diff(data, last_data)
    has_diff = len(diff['added']) != 0 or len(diff['updated']) != 0 or len(diff['removed']) != 0

    if has_diff:
        storage.write(data)

    oauth = OAuth1Session(
        os.environ['TWITTER_CONSUMER_KEY'],
        client_secret=os.environ['TWITTER_CONSUMER_SECRET'],
        resource_owner_key=os.environ['TWITTER_ACCESS_TOKEN'],
        resource_owner_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    )

    for d in diff['added'] + diff['updated']:
        try:
            run_task(d, oauth)
        except Exception as e:
            print('Error: {}'.format(e))

    return {
        'data': data,
        'diff': diff
    }
