import requests
import urllib.request
import re
import string

def download_page(url):
    try:
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        respData = str(resp.read())
        return respData
    except Exception as e:
        print(str(e))


def get_title(raw_html):
    starting_tag = r'<h1 id="firstHeading" class="firstHeading" lang="en">'
    ending_tag = '</h1>'

    starting_place = raw_html.find(starting_tag)
    ending_place = raw_html.find(ending_tag, starting_place + 1)
    return(raw_html[starting_place + 53 : ending_place])

def get_introduction(raw_html):
    starting_tag = r'<p>'
    ending_tag = '<div class="toctitle">'

    starting_place = raw_html.find(starting_tag)
    ending_place = raw_html.find(ending_tag, starting_place + 1)

    if '<div class="toctitle">' not in raw_html:
        ending_place = raw_html.find('</p>', starting_place + 1)
    else:
        pass

    return(raw_html[starting_place : ending_place])

def get_content(raw_html):
    starting_place = raw_html.find(r'<h2><span class="mw-headline" id=')
    starting_place_end = raw_html.find('>', starting_place + 1)
    ending_place = raw_html.find(r'<h2><span class="mw-headline" id="See_also">')

    content = raw_html[starting_place_end + 1 : ending_place]

    content_purged = re.sub(r'<.+?>', '', content)
    content_purged = content_purged.replace(r'\n', ' ')
    content_purged = re.sub(r'\[.+?\]', '', content_purged)
    content_purged = content_purged.translate(str.maketrans('','',string.punctuation))
    return(content_purged)


if __name__ == "__main__":
    url = "https://en.0wikipedia.org/index.php?q=aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvR3VtYm8"

    raw = download_page(url)
    print(url)
    print('====================')
    # print('Title')
    # print('====================')
    print(get_content(raw))
    # print('====================')
    # print('Introduction')
    # print('====================')
    # print(get_introduction(raw))
    # print('====================')
    # print('Introduction Purged')
    # print('====================')
    # print(re.sub(r'<.+?>', '', get_introduction(raw)))