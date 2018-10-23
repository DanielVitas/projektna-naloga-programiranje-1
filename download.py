import os
import re

import orodja
import folders

###############################################################################
# Naloži spletne strani iz rubrike: 'top anime'
###############################################################################


def top_url(index):
    return 'https://myanimelist.net/topanime.php?limit={}'.format(50 * index)


def top_name(index):
    return os.path.join('anime', 'top', 'html{}.html'.format(index))

# V primeru posodabljanja je trba posodbiti le range ter nastaviti vsili prenos na True

for i in range(265):  # 265 * 50 = 13250
    orodja.shrani_spletno_stran(top_url(i), top_name(i), vsili_prenos=False) 

###############################################################################
# Pridobi spletne naslove pravih strani in jih shrani
###############################################################################


top_pattern = re.compile(
    r'<span class="lightLink top-anime-rank-text rank\d+?">.*?'
    r'</span></div>', re.DOTALL)

href_pattern = re.compile(r'<a class="hoverinfo_trigger fl-l ml12 mr8" href="(?P<href>.+?)"')


def page_to_blocks(file_name, pattern):
    content = orodja.vsebina_datoteke(file_name)
    return [match.group(0) for match in pattern.finditer(content)]


def write_links_from_top(text_file=folders.links_name, directory=folders.top_directory):
    orodja.pripravi_imenik(folders.links_name)
    with open(text_file, 'w', encoding='utf-8') as file:
        for filename in os.listdir(directory):
            blocks = page_to_blocks(os.path.join(directory, filename), top_pattern)
            for block in blocks:
                result = href_pattern.search(block)
                if result:
                    file.write(result['href'] + '\n')

write_links_from_top()

###############################################################################
# Naloži spletne strani, katerih linki so zapisani v textovni datoteki
###############################################################################


def name(url):
    return os.path.join(folders.full_directory, url[url.rindex('/') + 1:] + '.html')


def download_pages(text_file=folders.links_name):
    with open(text_file, 'r', encoding='utf-8') as file:
        for line in file:
            orodja.shrani_spletno_stran(line.strip(), name(line.strip()))

download_pages()
