"""Fetch recent SEAO open-data JSON resources from the Données Québec CKAN API.
Conservative importer: omit records whose identity/status cannot be verified.
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

API = 'https://www.donneesquebec.ca/recherche/api/3/action/package_show?id=systeme-electronique-dappel-doffres-seao'
OUT = Path(__file__).resolve().parents[1] / 'opportunities.json'
HEADERS = {'User-Agent': 'SoumissionRadar/1.0 (public open-data importer)'}

def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=100) as response:
        return json.load(response)

def text(value):
    if isinstance(value, dict):
        return str(value.get('fr') or value.get('en') or next(iter(value.values()), ''))
    return str(value or '')

def date_only(value):
    value = text(value)
    match = re.search(r'\d{4}-\d{2}-\d{2}', value)
    return match.group(0) if match else ''

def extract_releases(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get('releases'), list):
            return payload['releases']
        if isinstance(payload.get('records'), list):
            return payload['records']
        if isinstance(payload.get('data'), list):
            return payload['data']
    if isinstance(payload, list):
        return payload
    return []

def normalize(record, today):
    if not isinstance(record, dict):
        return None
    tender = record.get('tender') or {}
    if not isinstance(tender, dict):
        return None
    status = text(tender.get('status')).lower()
    if status not in ('active', 'open', 'published'):
        return None
    title = text(tender.get('title') or record.get('title')).strip()
    deadline = date_only((tender.get('tenderPeriod') or {}).get('endDate'))
    if not title or not deadline or deadline < today:
        return None
    buyer = record.get('buyer') or {}
    buyer_name = text(buyer.get('name')) if isinstance(buyer, dict) else ''
    identifier = text(record.get('ocid') or record.get('id'))
    url = text(tender.get('url') or record.get('url'))
    if not url.startswith('https://'):
        url = ''
    if not identifier:
        return None
    description = text(tender.get('description'))
    haystack = (title+' '+description).lower()
    sectors = [('Électricité', ['électri', 'electric', 'éclairage', 'lighting']),('Construction', ['construction','rénovation','travaux','bâtiment']),('Informatique', ['informatique','logiciel','technologie']),('Services', ['service'])]
    sector = next((name for name, words in sectors if any(w in haystack for w in words)), 'Autres')
    region = ''
    locations = tender.get('deliveryLocations') or []
    if locations and isinstance(locations[0], dict):
        region = text(locations[0].get('description'))
    return {'id':identifier,'title':title[:250], 'buyer':buyer_name[:150], 'region':region[:100], 'sector':sector, 'deadline':deadline, 'url':url}

def main():
    catalog = get_json(API)
    if not catalog.get('success'):
        raise RuntimeError('CKAN did not return success')
    resources = catalog['result'].get('resources', [])
    recent = sorted((r for r in resources if re.match(r'hebdo_\d{8}_\d{8}\.json$', r.get('name',''))),key=lambda r:r['name'],reverse=True)[:5]
    if not recent:
        raise RuntimeError('No weekly SEAO JSON resources found; keeping previous data')
    today = dt.date.today().isoformat()
    items = {}
    processed = 0
    for resource in recent:
        url = resource.get('url','')
        if not url.startswith('https://'):
            continue
        payload = get_json(url)
        releases = extract_releases(payload)
        if not releases:
            print('Unsupported structure:',resource.get('name'))
            continue
        processed += 1
        for release in releases:
            item = normalize(release, today)
            if item:
                items[item['id']] = item
    if not processed:
        raise RuntimeError('No usable SEAO resources; previous data retained')
    # Do not publish empty data on schema mismatch; retain last successful snapshot.
    if not items:
        raise RuntimeError('No verified active tenders parsed; schema needs review')
    result = {'updated':today, 'source':'Données Québec / SEAO', 'items':sorted(items.values(),key=lambda x:x['deadline'])[:2000]}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved',len(result['items']),'open tenders')

if __name__=='__main__':
    main()
