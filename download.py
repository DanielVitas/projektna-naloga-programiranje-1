import csv
import json
import os
import re
import sys

import requests

###############################################################################
# Koda prof. Pretnarja
###############################################################################


def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)


def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print('Shranjujem {} ...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)
            print('shranjeno!')


def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()


def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)


def zapisi_json(objekt, ime_datoteke):
    '''Iz danega objekta ustvari JSON datoteko.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)

###############################################################################
# Moja koda
###############################################################################      

# Naloži spletne strani iz rubrike: 'top anime'

top_directory = os.path.join('anime', 'top')


def top_url(index):
    return 'https://myanimelist.net/topanime.php?limit={}'.format(50 * index)


def top_name(index):
    return os.path.join('anime', 'top', 'html{}.html'.format(index))

for i in range(2):
    shrani_spletno_stran(top_url(i), top_name(i))

# Pridobi spletne naslove pravih strani in jih shrani


links_name = os.path.join('data', 'links_to_anime.txt')

top_pattern = re.compile(
    r'<span class="lightLink top-anime-rank-text rank\d+?">.*?'
    r'</span></div>', re.DOTALL)

href_pattern = re.compile(r'<a class="hoverinfo_trigger fl-l ml12 mr8" href="(?P<href>.+?)"')


def page_to_blocks(file_name, pattern):
    content = vsebina_datoteke(file_name)
    return [match.group(0) for match in pattern.finditer(content)]


def write_links_from_top(text_file=links_name, directory=top_directory):
    pripravi_imenik(links_name)
    with open(text_file, 'w', encoding='utf-8') as file:
        for filename in os.listdir(directory):
            blocks = page_to_blocks(os.path.join(directory, filename), top_pattern)
            for block in blocks:
                result = href_pattern.search(block)
                if result:
                    file.write(result['href'] + '\n')

write_links_from_top()

# Naloži spletne strani, katerih linki so zapisani v textovni datoteki


full_directory = os.path.join('anime', 'full')


def name(url):
    return os.path.join(full_directory, url[url.rindex('/') + 1:] + '.html')


def download_pages(text_file=links_name):
    with open(text_file, 'r', encoding='utf-8') as file:
        for line in file:
            shrani_spletno_stran(line.strip(), name(line.strip()))

download_pages()

# Iz spletnih strani razbere podatke in naredi csv ter json


full_pattern = re.compile(
    r'<title>(?P<title>.*?)</title>.*?'
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

for m in full_pattern.finditer(vsebina_datoteke(os.path.join(full_directory, 'Death_Note.html'))):
    print(m.groupdict())
