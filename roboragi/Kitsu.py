import requests

AUTH_URL = 'https://kitsu.io/api/oauth/'
BASE_URL = 'https://kitsu.io/api/edge/'
ANIME_SEARCH_FILTER = 'anime?filter[text]='
MANGA_SEARCH_FILTER = 'manga?filter[text]='
ANIME_GET_FILTER = 'anime?filter[slug]='
MANGA_GET_FILTER = 'manga?filter[slug]='

session = requests.Session()
session.headers = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}


def search(endpoint, search_term, parser):
    try:
        response = session.get(BASE_URL + endpoint + search_term, timeout=4)
        response.raise_for_status()

        results = parser(response.json()['data'])

        if not results:
            return None

        return results
    except Exception as e:
        return None
    finally:
        session.close()


def search_anime(search_term):
    return search(ANIME_SEARCH_FILTER, search_term, parse_anime)


def search_manga(search_term):
    return search(MANGA_SEARCH_FILTER, search_term, parse_manga)


def search_light_novel(search_term):
    return search(MANGA_SEARCH_FILTER, search_term, parse_light_novel)


def get_anime(search_term):
    return search(ANIME_GET_FILTER, search_term, parse_anime)


def get_manga(search_term):
    return search(MANGA_GET_FILTER, search_term, parse_manga)


def get_light_novel(search_term):
    return search(MANGA_GET_FILTER, search_term, parse_light_novel)


def parse_anime(results):
    anime_list = []

    for entry in results:
        try:
            anime_list.append(dict(id=entry['id'],
                                   url='https://kitsu.io/anime/' + entry['attributes']['slug'],
                                   title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                                   title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                                   title_japanese=entry['attributes']['titles']['ja_jp'] if 'ja_jp' in entry['attributes']['titles'] else None,
                                   synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                                   episode_count=(int(entry['attributes']['episodeCount']) if int(entry['attributes']['episodeCount']) > 0 else None),
                                   type=entry['attributes']['showType'],
                                   description=entry['attributes']['synopsis'],
                                   nsfw=entry['attributes']['nsfw']))
        except AttributeError:
            pass

    return anime_list


def parse_manga(results):
    manga_list = []

    for entry in results:
        try:
            manga = dict(id=entry['id'],
                         url='https://kitsu.io/manga/' + entry['attributes']['slug'],
                         title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                         title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                         synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                         volume_count=(int(entry['attributes']['volumeCount']) if entry['attributes']['volumeCount'] else None),
                         chapter_count=(int(entry['attributes']['chapterCount']) if entry['attributes']['chapterCount'] else None),
                         type=entry['attributes']['mangaType'],
                         description=entry['attributes']['synopsis'])

            if manga['type'].lower() != 'novel':
                manga_list.append(manga)
        except AttributeError:
            pass

    return manga_list


def parse_light_novel(results):
    ln_list = []

    for entry in results:
        try:
            ln = dict(id=entry['id'],
                      url='https://kitsu.io/manga/' + entry['attributes']['slug'],
                      title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                      title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                      synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                      volume_count=(int(entry['attributes']['volumeCount']) if entry['attributes']['volumeCount'] else None),
                      chapter_count=(int(entry['attributes']['chapterCount']) if entry['attributes']['chapterCount'] else None),
                      type=entry['attributes']['mangaType'],
                      description=entry['attributes']['synopsis'])

            if ln['type'].lower() == 'novel':
                ln_list.append(ln)
        except AttributeError:
            pass

    return ln_list


def get_synonyms(result):
    synonyms = set()
    synonyms.add(result['title_romaji']) if result['title_romaji'] else None
    synonyms.add(result['title_english']) if result['title_english'] else None
    synonyms.update(result['synonyms'])
    return synonyms
