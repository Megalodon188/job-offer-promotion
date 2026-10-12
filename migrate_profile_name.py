"""Bounded profile-name migration after the coordinated ShowWorth product rename."""
import argparse
import datetime as dt
import os
from post import allowed_pds, rpc

DID = 'did:plc:rmvvl2twnwbculbftv6aebv6'
OLD = 'Revision Desk | Practical Tools'
NEW = 'ShowWorth Studio | Practical Tools'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not args.apply:
        print('Preview: replace the exact legacy display name with ' + NEW)
        return
    if dt.datetime.now(dt.timezone.utc).date() > dt.date(2026, 10, 13):
        print('Migration window closed; no changes.')
        return
    session = rpc('https://bsky.social', 'com.atproto.server.createSession',
                  {'identifier': os.environ['BSKY_HANDLE'].strip().lstrip('@'),
                   'password': os.environ['BSKY_APP_PASSWORD'].strip()})
    if session['did'] != DID:
        raise ValueError('Unexpected account')
    pds = 'https://bsky.social'
    for service in session.get('didDoc', {}).get('service', []):
        if service.get('type') == 'AtprotoPersonalDataServer':
            pds = service['serviceEndpoint'].rstrip('/')
    if not allowed_pds(pds):
        raise ValueError('Unexpected account server')
    token = session['accessJwt']
    params = {'repo': DID, 'collection': 'app.bsky.actor.profile', 'rkey': 'self'}
    current = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=params)
    profile = dict(current['value'])
    if profile.get('displayName') == NEW:
        print('ShowWorth profile name already present.')
        return
    if profile.get('displayName') != OLD:
        raise ValueError('Profile was independently changed; refusing to overwrite')
    profile['displayName'] = NEW
    rpc(pds, 'com.atproto.repo.putRecord',
        {**params, 'swapRecord': current['cid'], 'record': profile}, token=token)
    verified = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=params)
    if verified['value'].get('displayName') != NEW:
        raise ValueError('Profile-name verification failed')
    print('Verified ShowWorth profile name; all other profile fields preserved.')

if __name__ == '__main__':
    main()
