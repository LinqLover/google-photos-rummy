#!/usr/bin/env python3

from collections import Counter
import datetime as dt
import google_auth_oauthlib.flow
from pathlib import Path
import random
import requests
from tqdm import tqdm


def main(
    year,
    sample_size,
    max_width=4032,
    max_height=2268,
    output_dir='photos'
):
    """
    pre: 1900 <= year < 3000 and sample_size > 0 and max_width > 0 and max_height > 0 and len(output_dir) > 0
    post: True
    """
    min_date = dt.datetime(year=year, month=1, day=1)
    max_date = dt.datetime(year=year + 1, month=1, day=1)

    pictures = []
    number_of_accounts = 0
    # FIXME: requesting multiple accounts upfront is not working - new credentials appear to overwrite old ones
    while True:
        print(f"Google Photos Account{'' if not number_of_accounts else f' {len(number_of_accounts) + 1}'}:")
        credentials = authenticate()
        pictures += [
            {**picture, 'credentials': {'token': credentials.token}}
            for picture in get_pictures(credentials, min_date, max_date)
        ]
        if input("Add another account? (y/n): ") != 'y':
            break
        number_of_accounts += 1
    print(f"Fetched {len(pictures)} candidates")

    random_pictures = select_random_pictures(pictures, sample_size)
    print(f"Selected {len(random_pictures)} random photos")

    download_count = download_pictures(random_pictures, max_width, max_height, output_dir)
    print(f"Downloaded {download_count} photos to {output_dir}!")

def authenticate():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'])

    return flow.run_console()

def get_pictures(credentials, min_date, max_date):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems'
    params = {
        'pageSize': 100
    }

    pictures = []

    page = 0
    resp = None
    print("Fetching photos...")
    # Loop until we have all the photos
    while not resp or 'nextPageToken' in resp.json():
        page += 1
        print('Page', page)
        if resp:
            params['pageToken'] = resp.json()['nextPageToken']
        resp = requests.get(url, params=params,
                            headers={'Authorization': 'Bearer ' + credentials.token})
        new_pictures = resp.json()['mediaItems']
        new_pictures = [
            picture for picture in new_pictures
            # exclude videos
            if picture['mimeType'].startswith('image')
               # exclude special creations
               and not any(
                exclude in picture['filename']
                for exclude in ['PANO', 'PHOTOSPHERE', 'POP_OUT', 'COLLAGE'])
        ]
        for picture in new_pictures:
            try:
                picture['date'] = dt.datetime.strptime(
                    picture['mediaMetadata']['creationTime'],
                    '%Y-%m-%dT%H:%M:%SZ'
                )
            except ValueError:
                picture['date'] = dt.datetime.strptime(
                    picture['mediaMetadata']['creationTime'],
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
        pictures += new_pictures
        if min(picture['date'] for picture in pictures) < min_date:
            break

    return [
        picture for picture in pictures
        if min_date <= picture['date'] < max_date
    ]

def select_random_pictures(pictures, sample_size):
    # return random.sample(pictures, min(sample_size, len(pictures)))

    # advanced sampling: select pictures from each day with equal probability
    if not pictures:
        return []
    date_counts = Counter(picture['date'].date() for picture in pictures)
    return random.choices(
        pictures,
        k=min(sample_size, len(pictures)),
        weights=[
            1 / date_counts[picture['date'].date()]
            for picture in pictures
        ]
    )

def download_pictures(pictures, max_width, max_height, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    download_count = 0
    for picture in tqdm(pictures, desc="Downloading"):
        url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture['id']}"
        credentials = picture['credentials']
        resp = requests.get(url, headers={'Authorization': 'Bearer ' + credentials['token']})
        try:
            filename = resp.json()['filename']
            file_url = resp.json()['baseUrl'] + f'=w{max_width}-h{max_height}'
            resp = requests.get(file_url, headers={'Authorization': 'Bearer ' + credentials['token']})
            with open(f'{output_dir}/{filename}', 'wb') as file:
                file.write(resp.content)
            download_count += 1
        except Exception as ex:
            print("Failed to download", picture['id'], ex)
            print(resp.json())
    return download_count


if __name__ == "__main__":
    print("Google Photos Rummy")
    print()

    year = (dt.datetime.now() - dt.timedelta(days=30 * 9)).year
    year = int(input(f"Year ({year}): ") or year)
    sample_size = 50
    sample_size = int(input(f"Sample Size ({sample_size}): ") or sample_size)

    main(year, sample_size)
