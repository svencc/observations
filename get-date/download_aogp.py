"""Download the current public AOGP free-books catalog and its PDF endpoints."""
from concurrent.futures import ThreadPoolExecutor
import json
from download_sources import fetch, links, ROOT

URL='https://www.ao-gp.org/scientology-free-books-pdfs-by-l-ron-hubbard'
if __name__=='__main__':
    row,_=fetch(('aogp',URL,'web search for current free books catalog','en',0))
    if row['status']!='successful':print(json.dumps(row));raise SystemExit(1)
    urls=[u for u in links((ROOT/row['local_path']).read_text(errors='replace'),URL) if '/api/books/pdf/' in u]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row,_ in pool.map(fetch,[('aogp',u,URL,'en',0) for u in urls]):
            print(json.dumps({k:row.get(k) for k in ['source_url','status','bytes','error']}),flush=True)
