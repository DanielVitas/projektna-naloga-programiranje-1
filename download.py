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
links_name = os.path.join('data', 'links_to_anime.txt')


def top_url(index):
    return 'https://myanimelist.net/topanime.php?limit={}'.format(50 * index)


def top_name(index):
    return os.path.join('anime', 'top', 'html{}.html'.format(index))

for i in range(2):
    shrani_spletno_stran(top_url(i), top_name(i))

# Pridobi spletne naslove pravih strani in jih shrani


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
