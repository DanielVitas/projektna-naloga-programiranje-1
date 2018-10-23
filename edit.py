import os
import re
from datetime import datetime

import orodja
import folders

###############################################################################
# Ekstrakcija podatkov
###############################################################################


full_pattern = re.compile(
    r'<meta property="og:title" content="(?P<title>.*?)">.*?'
    r'<meta property="og:url" content="https://myanimelist.net/anime/(?P<id>.*?)/.*?'
    r'<meta property="og:description" content="(?P<description>.*?)">.*?'
    r'Type:</span>\s*?<a href="(.*?)">(?P<type>.*?)</a></div>.*?'
    r'Episodes:</span>(?P<episodes>.*?)<.*?'
    r'Status:</span>(?P<status>.*?)<.*?'
    r'Aired:</span>(?P<aired>.*?)<.*?'

    r'Producers:</span>(?P<producers>.*?)</div>.*?'
    r'Studios:</span>(?P<studios>.*?)</div>.*?'

    r'Source:</span>(?P<source>.*?)</div>.*?'

    r'Genres:</span>(?P<genres>.*?)</div>.*?'

    r'Duration:</span>(?P<duration>.*?)</div>.*?'
    r'Rating:</span>(?P<rating>.*?)</div>.*?'

    r'Score:</span>\s*?<span itemprop="(.*?)">(?P<score>.*?)<.*?'
    r'Ranked:</span>\s*?#(?P<rank>\d*?)<.*?'
    r'Popularity:</span>\s*?#(?P<popularity>.*?)</div>.*?'
    r'Members:</span>(?P<members>.*?)</div>.*?'
    r'Favorites:</span>(?P<favorites>.*?)</div>.*?',
    re.DOTALL
)

producer_pattern = re.compile(r'<a href="/anime/producer/(?P<id>\d*?)/.*?" title=".*?">(?P<name>.*?)</a>')
genres_pattern = re.compile(r'<a href="/anime/genre/(?P<id>\d*?)/.*?" title=".*?">(?P<name>.*?)</a>')


def aired_extract(aired):
    a = aired.split(" to ")
    try:
        date_from = datetime.strptime(a[0], '%b %d, %Y')
    except ValueError:
        date_from = None
    try:
        date_to = datetime.strptime(a[1], '%b %d, %Y')
    except (ValueError, IndexError):
        date_to = None
    return (date_from, date_to)


def producers_extract(text):
    producers = []
    for match in producer_pattern.finditer(text):
        id = int(match.groupdict()['id'])
        producers.append({'id': id, 'name': match.groupdict()['name']})
    return producers


def genres_extract(text):
    genres = []
    for match in genres_pattern.finditer(text):
        id = int(match.groupdict()['id'])
        genres.append({'id': id, 'name': match.groupdict()['name']})
    return genres


def clean_info(info):
    info['title'] = info['title'].strip()
    info['id'] = int(info['id'])
    info['description'] = info['description']
    info['type'] = info['type'].strip()
    try:
        info['episodes'] = int(info['episodes'])
    except ValueError:
        info['episodes'] = None
    info['status'] = info['status'].strip()

    a = aired_extract(info['aired'].strip())
    info['airedfrom'] = a[0]
    info['airedto'] = a[1]
    info.pop('aired')

    info['producers'] = producers_extract(info['producers'])
    info['studios'] = producers_extract(info['studios'])
    info['source'] = info['source'].strip()
    info['genres'] = genres_extract(info['genres'])

    info['duration'] = info['duration'].strip()
    info['rating'] = info['rating'].strip()
    try:
        info['score'] = float(info['score'])
    except ValueError:
        info['score'] = None
    try:
        info['rank'] = int(info['rank'])
    except ValueError:
        info['rank'] = None
    try:
        info['popularity'] = int(info['popularity'])
    except ValueError:
        info['popularity'] = None
    try:
        info['members'] = float(info['members'].replace(',', '.'))
    except ValueError:
        info['members'] = None
    try:
        info['favorites'] = float(info['favorites'].replace(',', '.'))
    except ValueError:
        info['members'] = None
    return info

###############################################################################
# Ustvari linked liste za csv
###############################################################################


def get_linked_lists(anime_list):
    producers, genres = [], []
    producers_seen, genres_seen = set(), set()
    studio_list, producer_list, genre_list = [], [], []
    for anime in anime_list:
        for studio in anime.pop('studios'):
            if studio['id'] not in producers_seen:
                producers_seen.add(studio['id'])
                producers.append(studio)
            studio_list.append({'anime': anime['id'], 'studio': studio['id']})
        for producer in anime.pop('producers'):
            if producer['id'] not in producers_seen:
                producers_seen.add(producer['id'])
                producers.append(producer)
            producer_list.append({'anime': anime['id'], 'producer': producer['id']})
        for genre in anime.pop('genres'):
            if genre['id'] not in producers_seen:
                genres_seen.add(genre['id'])
                genres.append(genre)
            genre_list.append({'anime': anime['id'], 'genre': genre['id']})
    producers.sort(key=lambda producer: producer['id'])
    genres.sort(key=lambda genre: genre['id'])
    studio_list.sort(key=lambda link: (link['studio'], link['anime']))
    producer_list.sort(key=lambda link: (link['anime'], link['producer']))
    genre_list.sort(key=lambda link: (link['anime'], link['genre']))
    return producers, genres, studio_list, producer_list, genre_list

###############################################################################
# Zapiše podatke v json in csv
###############################################################################


def create_data(directory=folders.full_directory, json=True, csv=True):
    anime_list = []
    for filename in os.listdir(directory):
        content = orodja.vsebina_datoteke(os.path.join(directory, filename))
        result = full_pattern.search(content)
        if result:
            anime_list.append(clean_info(result.groupdict()))
    anime_list.sort(key=lambda anime: anime['id'])
    if json:
        orodja.zapisi_json(anime_list, folders.json_name)
    if csv:
        producers, genres, studio_list, producer_list, genre_list = get_linked_lists(anime_list)
        orodja.zapisi_csv(anime_list, ['id', 'title', 'score', 'airedfrom', 'airedto',
        'episodes', 'type', 'status', 'source', 'rating', 'members', 'duration', 'rank',
        'popularity', 'favorites', 'description'], folders.csv_name)
        orodja.zapisi_csv(producers, ['id', 'name'], folders.csv_producers_name)
        orodja.zapisi_csv(genres, ['id', 'name'], folders.csv_genres_name)
        orodja.zapisi_csv(studio_list, ['studio', 'anime'], folders.csv_linked_studios_name)
        orodja.zapisi_csv(producer_list, ['anime', 'producer'], folders.csv_linked_producers_name)
        orodja.zapisi_csv(genre_list, ['anime', 'genre'], folders.csv_linked_genres_name)

create_data()
