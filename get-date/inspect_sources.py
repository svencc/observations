"""Read public source catalogs; no login or account actions."""
import concurrent.futures
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'stss': 'https://stss.nl/materials/',
    'freezone-de': 'https://www.freezone.de/publikationen-vortraege-seminare/',
    'freezone-org': 'https://freezone.org/Content/CBR/Publications/publications.html',
    'project-avalon': 'https://projectavalon.net/lib/',
    'sptv-drive': 'https://resources.sptv.space/list/lrh/',
    'saentowiki': 'https://saentowiki.com/en/contents/home',
    'scientolipedia': 'https://www.scientolipedia.org/info/Having_the_Correct_Technology',
    'galac-patra': 'https://0-48.ru/',
    'sciento': 'https://sciento.org/',
}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a' and d.get('href'):
            self.hrefs.append(d['href'])

def inspect(item):
    source, url = item
    out = ROOT / 'raw-data' / source / '_provenance' / 'catalog'
    out.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, timeout=(15, 60))
        (out / 'entry.html').write_bytes(r.content)
        p = Links(); p.feed(r.text)
        links = list(dict.fromkeys(urljoin(r.url, h) for h in p.hrefs))
        (out / 'links.json').write_text(json.dumps(links, indent=2))
        return source, r.status_code, len(r.content), len(links)
    except Exception as e:
        return source, str(e)

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(inspect, SOURCES.items()):
            print(json.dumps(result), flush=True)
