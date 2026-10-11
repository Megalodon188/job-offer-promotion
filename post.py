"""Post one dated promotion to your own Bluesky account. No dependencies."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
COLLECTION = 'app.bsky.feed.post'

class APIError(Exception):
    def __init__(self, status, code, method=None):
        super().__init__(f'Bluesky HTTP {status}: {code}' + (f' during {method}' if method else ''))
        self.status, self.code = status, code

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

def rpc(host, method, data=None, token=None, params=None):
    url = host + '/xrpc/' + method
    if params:
        url += '?' + urllib.parse.urlencode(params)
    headers = {'Content-Type': 'application/json', 'User-Agent': 'JobOfferPromotion/1.0'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            code = json.loads(exc.read()).get('error', 'RequestFailed')
        except (ValueError, UnicodeDecodeError):
            code = 'RequestFailed'
        # Never print authentication response bodies or tokens.
        raise APIError(exc.code, code, method) from None

def allowed_pds(url):
    p = urllib.parse.urlsplit(url)
    return (p.scheme == 'https' and not p.username and not p.password
            and p.port in (None, 443) and p.path in ('', '/') and not p.query and not p.fragment
            and (p.hostname == 'bsky.social' or (p.hostname or '').endswith('.bsky.network')))

def make_record(body, url, date, label='$5 calculator'):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port:
        raise ValueError('Use an approved HTTPS product or demo link.')
    payhip = p.hostname == 'payhip.com' and p.path.startswith('/b/') and len(p.path) >= 4
    demo = (p.hostname == 'revision-desk-demo.quietgrass17.chatgpt.site'
            and p.path in ('', '/') and not p.query and not p.fragment)
    if not (payhip or demo):
        raise ValueError('Use the Payhip product link or the approved Revision Desk demo.')
    text = body + '\n\n' + label + ': ' + url
    if len(text) > 300 or len(text.encode()) > 3000:
        raise ValueError('Post is too long. Shorten the content or product URL.')
    start = len(text[:text.rfind(url)].encode('utf-8'))
    record = {'$type': COLLECTION, 'text': text, 'langs': ['en'],
            'createdAt': date.isoformat() + 'T18:17:00.000Z',
            'facets': [{'index': {'byteStart': start, 'byteEnd': start + len(url.encode('utf-8'))},
                        'features': [{'$type': 'app.bsky.richtext.facet#link', 'uri': url}]}]}
    for match in re.finditer(r'(?<![\w])#([A-Za-z][A-Za-z0-9_]{0,63})\b', text):
        record['facets'].append({
            'index': {'byteStart': len(text[:match.start()].encode('utf-8')),
                      'byteEnd': len(text[:match.end()].encode('utf-8'))},
            'features': [{'$type': 'app.bsky.richtext.facet#tag', 'tag': match.group(1)}]})
    return record

def publish(record, rkey, handle, password, api=rpc):
    handle, password = handle.strip(), password.strip()
    if not handle or not re.fullmatch(r'[A-Za-z0-9]{4}(?:-[A-Za-z0-9]{4}){3}', password):
        raise ValueError('Set BSKY_HANDLE and a Bluesky App Password in GitHub Secrets.')
    session = api('https://bsky.social', 'com.atproto.server.createSession',
                  {'identifier': handle.lstrip('@'), 'password': password})
    pds = 'https://bsky.social'
    for service in session.get('didDoc', {}).get('service', []):
        if service.get('type') == 'AtprotoPersonalDataServer':
            pds = service['serviceEndpoint'].rstrip('/')
            break
    if not allowed_pds(pds):
        raise ValueError('This starter supports Bluesky-hosted accounts only.')
    params = {'repo': session['did'], 'collection': COLLECTION, 'rkey': rkey}
    try:
        api(pds, 'com.atproto.repo.getRecord', token=session['accessJwt'], params=params)
        return 'Already posted for this campaign day. No duplicate created.'
    except APIError as exc:
        if exc.code != 'RecordNotFound':
            raise
    result = api(pds, 'com.atproto.repo.createRecord',
                 {**params, 'record': record}, token=session['accessJwt'])
    return 'Published: ' + result['uri']

def daily_rkey(date, clock_id=1023):
    # A valid TID, stable for this campaign's UTC day so retries cannot duplicate it.
    epoch = dt.date(1970, 1, 1)
    micros = (date - epoch).days * 86_400_000_000
    if not 0 <= clock_id <= 1023:
        raise ValueError("Campaign clock ID must be between 0 and 1023.")
    value = (micros << 10) | clock_id
    alphabet = '234567abcdefghijklmnopqrstuvwxyz'
    return ''.join(alphabet[(value >> shift) & 31] for shift in range(60, -1, -5))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.dry_run and os.getenv('PROMOTION_ENABLED', '').lower() != 'true':
        print('Disabled. Set PROMOTION_ENABLED=true after previewing the posts.')
        return
    start = dt.date.fromisoformat(os.environ['CAMPAIGN_START_DATE'])
    today = dt.datetime.now(dt.timezone.utc).date()
    index = (today - start).days
    posts = json.loads((ROOT / os.getenv('POSTS_FILE', 'posts.json')).read_text())
    if index < 0:
        print('Campaign has not started.')
        return
    if index >= len(posts):
        print('30-day campaign finished. No post sent. Extend posts.json for another campaign.')
        return
    record = make_record(posts[index], os.environ['PRODUCT_URL'], today, os.getenv('POST_LABEL', '$5 calculator'))
    rkey = daily_rkey(today, int(os.getenv('CAMPAIGN_CLOCK_ID', '1023')))
    if args.dry_run:
        print(f'Preview day {index + 1}/{len(posts)}:\n{record["text"]}')
        return
    record['createdAt'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    print(publish(record, rkey, os.getenv('BSKY_HANDLE', ''), os.getenv('BSKY_APP_PASSWORD', '')))

if __name__ == '__main__':
    try:
        main()
    except (APIError, ValueError, KeyError, OSError) as exc:
        print(f'Posting stopped: {exc}', file=sys.stderr)
        sys.exit(1)
