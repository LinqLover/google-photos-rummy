#!/usr/bin/env python3

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

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'])

    credentials = flow.run_console()

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
        for picture in new_pictures:
            picture['date'] = dt.datetime.strptime(
                picture['mediaMetadata']['creationTime'],
                '%Y-%m-%dT%H:%M:%SZ'
            )
        pictures += new_pictures
        if min(picture['date'] for picture in pictures) < min_date:
            break

    pictures = [
        picture for picture in pictures
        if min_date <= picture['date'] < max_date
    ]
    print(f"Fetched {len(pictures)} candidates")

    random_pictures = random.sample(pictures, sample_size)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    download_count = 0
    for picture in tqdm(random_pictures, desc="Downloading"):
        url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture['id']}"
        resp = requests.get(url, headers={'Authorization': 'Bearer ' + credentials.token})
        try:
            filename = resp.json()['filename']
            file_url = resp.json()['baseUrl'] + f'=w{max_width}-h{max_height}'
            resp = requests.get(file_url, headers={'Authorization': 'Bearer ' + credentials.token})
            with open(f'{output_dir}/{filename}', 'wb') as file:
                file.write(resp.content)
            download_count += 1
        except Exception as ex:
            print("Failed to download", picture['id'], ex)
            print(resp.json())

    print(f"Downloaded {download_count} photos to {output_dir}!")

if __name__ == "__main__":
    print("Google Photos Rummy")
    print()

    year = (dt.datetime.now() - dt.timedelta(days=30 * 9)).year
    year = int(input(f"Year ({year}): ") or year)
    sample_size = 50
    sample_size = int(input(f"Sample Size ({sample_size}): ")) or sample_size

    main(year, sample_size)
