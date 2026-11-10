"""Read-only inventory comparison; filename matches are candidates, not proof."""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '0-get-data/overlap-assessment'


def filename(row):
    target = parse_qs(urlsplit(row['source_url']).query).get('download', [''])[0]
    return target or row.get('original_filename') or Path(row.get('local_path', '')).name


def key(name, relaxed=False):
    name = unicodedata.normalize('NFKC', name).casefold()
    suffix = Path(name).suffix
    stem = name[:-len(suffix)] if suffix else name
    if relaxed:
        stem = re.sub(r'\bocr\b', '', stem)
    stem = ''.join(c for c in stem if c.isalnum())
    if len(stem) < 10 or stem in ('titleunknown', 'titleunkown'):
        return None
    return stem + suffix


def main():
    OUT.mkdir(exist_ok=True)
    rows = [json.loads(l) for l in (ROOT / '0-get-data/download-manifest.jsonl').read_text().splitlines()]
    by_path = {}
    by_url = {}
    for r in rows:
        by_url[(r['source_id'], r['source_url'])] = r
        if r.get('local_path'):
            by_path[r['local_path']] = r
    local = [r for r in by_path.values() if r['status'] == 'successful'
             and r.get('sha256') and r.get('kind') == 'document']
    indexes = [defaultdict(list), defaultdict(list)]
    non_drive_hashes = defaultdict(list)
    for r in local:
        if r['source_id'] == 'sptv-drive':
            continue
        non_drive_hashes[r['sha256']].append(r)
        for index, relaxed in zip(indexes, (False, True)):
            k = key(filename(r), relaxed)
            if k:
                index[k].append(r)

    def assess(name):
        for label, index, relaxed in zip(('normalized_filename', 'ocr_variant_filename'), indexes, (False, True)):
            candidates = index.get(key(name, relaxed), [])
            if candidates:
                unique = {r['sha256']: r for r in candidates}
                return dict(classification=label, distinct_local_hashes=len(unique),
                            candidates=[dict(source=r['source_id'], name=filename(r),
                                             path=r['local_path'], sha256=r['sha256'])
                                        for r in list(unique.values())[:5]])
        return dict(classification='no_filename_match', candidates=[])

    inventory = {}
    for f in ('drive-inventory.json', 'extra-drive-inventory.json'):
        for entry in json.loads((ROOT / 'raw-data/sptv-drive/_provenance' / f).read_text()):
            inventory[entry[0]] = entry
    missing = []; downloaded = []; calibration = Counter()
    for fid, name, mime, parent in inventory.values():
        url = 'https://drive.google.com/file/d/' + fid + '/view'
        old = by_url.get(('sptv-drive', url), {})
        if old.get('status') == 'successful' and old.get('sha256'):
            downloaded.append(old)
            if old['sha256'] in non_drive_hashes:
                calibration['byte_identical_copy_elsewhere'] += 1
            match = assess(name)
            if match['classification'] != 'no_filename_match':
                calibration['filename_candidates'] += 1
                if any(r['sha256'] == old['sha256'] for r in indexes[0].get(key(name), []) + indexes[1].get(key(name, True), [])):
                    calibration['filename_and_hash_match'] += 1
                else:
                    calibration['filename_but_no_identical_hash'] += 1
            continue
        missing.append(dict(drive_id=fid, name=name, mime=mime, parent=parent,
                            prior_status=old.get('status', 'unattempted'), **assess(name)))
    counts = Counter(r['classification'] for r in missing)
    assert len(missing) + len(downloaded) == len(inventory)
    assert sum(counts.values()) == len(missing)
    (OUT / 'missing-drive-candidates.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in missing))

    lrh_missing = []
    for line in (ROOT / 'raw-data/_handover/pending-lrhmaterials.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r['kind'] != 'download':
            continue
        old = by_url.get(('lrhmaterials', r['source_url']), {})
        if old.get('status') != 'successful':
            name = filename(r)
            lrh_missing.append(dict(name=name, url=r['source_url'], prior_status=old.get('status', 'unattempted'), **assess(name)))
    (OUT / 'missing-lrh-candidates.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in lrh_missing))
    summary = dict(created_at=datetime.now(timezone.utc).isoformat(), method='Saved inventory and validated manifest only; no new downloads, rehashing, extraction or content comparison.',
                   drive_inventory=len(inventory), drive_downloaded=len(downloaded), drive_missing=len(missing),
                   missing_drive_classifications=dict(counts),
                   missing_drive_prior_statuses=dict(Counter(r['prior_status'] for r in missing)),
                   calibration_on_downloaded_drive=dict(calibration),
                   lrh_missing=len(lrh_missing), missing_lrh_classifications=dict(Counter(r['classification'] for r in lrh_missing)),
                   limitations=['Missing Drive inventories provide no checksum or byte size.',
                                'Matching filenames, even without OCR suffix, do not prove identical contents or editions.',
                                'No filename match does not establish that the work is absent; archives and different names are not resolved.',
                                'The downloaded Drive subset is not a random sample; do not extrapolate its overlap percentage.',
                                'No complete bibliography is available to prove a complete LRH/CBR collected edition.'])
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
