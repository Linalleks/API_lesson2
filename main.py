import requests
from decouple import config
from urllib.parse import urlparse


def shorten_link(token, url):
    base_url = 'https://api.vk.ru/method/utils.getShortLink'
    response = requests.get(base_url, params={
        'v': '5.199',
        'access_token': token,
        'url': url
    })
    response.raise_for_status()
    response = response.json()

    if 'error' in response:
        raise requests.exceptions.HTTPError('Указана некорректная ссылка. '
                                            + 'Невозможно её сократить.')

    short_url = response['response']['short_url']
    return short_url


def count_clicks(token, link):
    base_url = 'https://api.vk.ru/method/utils.getLinkStats'
    response = requests.get(base_url, params={
        'v': '5.199',
        'access_token': token,
        'key': link,
        'interval': 'forever'
    })
    response.raise_for_status()
    response = response.json()

    if 'error' in response:
        raise requests.exceptions.HTTPError('Указана некорректная ссылка.')

    if response['response']['stats'] == []:
        clicks_count = 0
    else:
        clicks_count = response['response']['stats'][0]['views']

    return clicks_count


def is_short_link_vk(token, url):
    base_url = 'https://api.vk.ru/method/utils.checkLink'
    response = requests.get(base_url, params={
        'v': '5.199',
        'access_token': token,
        'url': url
    })
    response.raise_for_status()
    response = response.json()

    if 'error' in response:
        raise requests.exceptions.HTTPError('Указана некорректная ссылка.')

    return (response['response']['link'] != url) \
        & (urlparse(url).netloc == 'vk.cc')


def main():
    token = config('TOKEN_API_VK')
    print('Приложение сократит длинную ссылку',
          'или предоставит статистику кликов по короткой ссылке.')
    try:
        user_url = input('Введите ссылку: ')
        if is_short_link_vk(token, user_url):
            path_link = urlparse(user_url).path[1:]
            number_clicks = count_clicks(token, path_link)
            print('Количество кликов по ссылке: ', number_clicks)
        else:
            short_link = shorten_link(token, user_url)
            print('Сокращенная ссылка: ', short_link)
    except requests.exceptions.HTTPError as error:
        raise SystemExit(f'Произошла ошибка:\n{error}')


if __name__ == '__main__':
    main()
