#!/usr/bin/env python3

from collections import Counter
import datetime as dt
import exifread
from functools import cached_property
import google_auth_oauthlib.flow
from pathlib import Path
import random
import requests
import shutil
from tqdm import tqdm


class PictureRepository:
    @staticmethod
    def create():
        raise NotImplementedError()

    def get_pictures(self, min_date, max_date):
        raise NotImplementedError()


class Picture:
    @property
    def date(self):
        raise NotImplementedError()

    def download(self, max_width, max_height, output_dir):
        raise NotImplementedError()


class GooglePhotosRepository(PictureRepository):
    @staticmethod
    def create():
        name = input("Name: ")
        return GooglePhotosRepository(name)

    def __init__(self, name):
        self.name = name
        self.credentials = None

    def get_pictures(self, min_date, max_date):
        # FIXME: requesting multiple accounts upfront is not working - new credentials appear to overwrite old ones
        self.credentials = self.authenticate()

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
            print("Page", page)
            if resp:
                params['pageToken'] = resp.json()['nextPageToken']
            resp = requests.get(url, params=params,
                                headers={'Authorization': 'Bearer ' + self.credentials.token})
            media_items = resp.json()['mediaItems']
            pictures += [
                GooglePhoto(media_item, self)
                for media_item in media_items
                # exclude videos
                if media_item['mimeType'].startswith('image')
                # exclude special creations
                and not any(
                    exclude in media_item['filename']
                    for exclude in ['PANO', 'PHOTOSPHERE', 'POP_OUT', 'COLLAGE'])
            ]
            if min(picture.date for picture in pictures) < min_date:
                break

        return [
            picture
            for picture in pictures
            if min_date <= picture.date < max_date
        ]

    def authenticate(self):
        print(f"Authenticating account {self.name}...")
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'])

        return flow.run_console()

    def download_picture(self, media_item, max_width, max_height, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{media_item['id']}"
        resp = requests.get(url, headers={'Authorization': 'Bearer ' + self.credentials.token})
        try:
            filename = resp.json()['filename']
            file_url = resp.json()['baseUrl'] + f'=w{max_width}-h{max_height}'
            resp = requests.get(file_url, headers={'Authorization': 'Bearer ' + self.credentials.token})
            with open(f'{output_dir}/{filename}', 'wb') as file:
                file.write(resp.content)
        except Exception as ex:
            print("Failed to download", media_item['id'], ex)
            print(resp.json())
            return False
        return True


class GooglePhoto(Picture):
    def __init__(self, media_item, repository):
        self.media_item = media_item
        self.repository = repository

    @cached_property
    def date(self):
        creation_time = self.media_item['mediaMetadata']['creationTime']
        try:
            return dt.datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return dt.datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    def download(self, max_width, max_height, output_dir):
        return self.repository.download_picture(self.media_item, max_width, max_height, output_dir)


class FileRepository(PictureRepository):
    @staticmethod
    def create():
        path = input("Path: ")
        if not path:
            raise ValueError("Path is required")
        return FileRepository(path)

    def __init__(self, path):
        self.path = Path(path)

    def get_pictures(self, min_date, max_date):
        pictures = [
            FilePicture(file)
            for ext in ['jpg', 'jpeg']
            for file in self.path.glob(f'**/*.{ext}')
        ]

        return [
            picture
            for picture in pictures
            if min_date <= picture.date < max_date
        ]


class FilePicture(Picture):
    def __init__(self, path):
        self.path = Path(path)

    @cached_property
    def date(self):
        try:
            with open(self.path.as_posix(), 'rb') as f:
                exif = exifread.process_file(f)
                return dt.datetime.strptime(str(exif['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
        except Exception as ex:
            import pdb; pdb.set_trace()
            print(f"Warning: Failed to read EXIF data for {self.path} ({ex}), using file modification time")
            return dt.datetime.fromtimestamp(self.path.stat().st_mtime)

    def download(self, max_width, max_height, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.path, f'{output_dir}')
        return True


def main(
    repositories,
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

    pictures = [
        picture
        for repository in tqdm(repositories, desc="Finding photos")
        for picture in repository.get_pictures(min_date, max_date)
    ]
    print(f"Fetched {len(pictures)} candidates")

    random_pictures = select_random_pictures(pictures, sample_size)
    print(f"Selected {len(random_pictures)} random photos")

    download_count = len([
        picture
        for picture in tqdm(random_pictures, desc="Downloading photos")
        if picture.download(max_width, max_height, output_dir)
    ])
    print(f"Downloaded {download_count} photos to {output_dir}!")


def select_random_pictures(pictures, sample_size):
    # return random.sample(pictures, min(sample_size, len(pictures)))

    # advanced sampling: avoid selecting multiple photos from the same day
    # TODO: consider explicit scene duplication (e.g., day + hour)
    uniform_weight = 0.8  # weight for uniform sampling (fair representation of holidays)
    daily_weight = 0.2  # weight for daily sampling (promote diversity/everyday photos)
    if not pictures:
        return []
    date_counts = Counter(picture.date.date() for picture in pictures)
    return random.choices(
        pictures,
        k=min(sample_size, len(pictures)),
        weights=[
            (
                uniform_weight
                + daily_weight / date_counts[picture.date.date()]
            )
            for picture in pictures
        ]
    )


if __name__ == "__main__":
    print("Google Photos Rummy")
    print()

    year = (dt.datetime.now() - dt.timedelta(days=30 * 9)).year
    year = int(input(f"Year ({year}): ") or year)
    sample_size = 50
    sample_size = int(input(f"Sample Size ({sample_size}): ") or sample_size)
    output_dir = 'photos'
    output_dir = input(f"Output Directory ({output_dir}): ") or output_dir

    repository_types = {
        'google_photos': GooglePhotosRepository,
        'files': FileRepository,
    }
    repositories = []
    while True:
        repository_type = input(f"Repository{'' if not repositories else f' {len(repositories) + 1}'} ({'/'.join(repository_types.keys())}): ")
        if not repository_type:
            break
        repository = repository_types[repository_type].create()
        repositories.append(repository)
        if input("Add another repository? (y/n): ") != 'y':
            break
    print()

    main(repositories, year, sample_size, output_dir=output_dir)
