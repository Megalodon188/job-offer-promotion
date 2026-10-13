"""One-time exact-match migration of our own Bluesky bio and pinned introduction."""
import datetime as dt
import os
from post import allowed_pds, daily_rkey, make_record, rpc

DID = 'did:plc:rmvvl2twnwbculbftv6aebv6'
DEMO = 'https://revision-desk-demo.quietgrass17.chatgpt.site'
OLD_DESCRIPTION = ('Practical tools for work and freelance editing. Free revision-cost check: ' +
                   DEMO + ' | Paid downloads on Payhip. Automated product updates.')
NEW_DESCRIPTION = ('Practical tools for freelance editing, pricing and client approvals. ' +
                   'Free ShowWorth tools: ' + DEMO +
                   ' | Paid desktop downloads on Payhip. Automated product updates.')
OLD_BODY = ('Fixed-price video editors: try this free revision-cost check. Enter your price and hours '
            'to see how extra time changes your effective pay. No email gate. Full paid tool is optional. '
            '#VideoEditing #Freelance')
NEW_BODY = ('Fixed-price video editors: use ShowWorth’s free tools to check revision cost or draft an '
            'extra-work quote. No email gate. The paid desktop toolkit is optional. '
            '#VideoEditing #Freelance')
RKEY = daily_rkey(dt.date(2026, 10, 11), 1021)

def main():
    if dt.datetime.now(dt.timezone.utc).date() > dt.date(2026, 10, 14):
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
    profile_params = {'repo': DID, 'collection': 'app.bsky.actor.profile', 'rkey': 'self'}
    post_params = {'repo': DID, 'collection': 'app.bsky.feed.post', 'rkey': RKEY}
    profile_current = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=profile_params)
    post_current = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=post_params)
    profile = dict(profile_current['value'])
    post = dict(post_current['value'])
    old_text = make_record(OLD_BODY, DEMO, dt.date(2026, 10, 11), 'Free tool')['text']
    new_record = make_record(NEW_BODY, DEMO, dt.date(2026, 10, 11), 'Free ShowWorth tools')
    if profile.get('description') == NEW_DESCRIPTION and post.get('text') == new_record['text']:
        print('ShowWorth bio and pinned introduction already aligned.')
        return
    if profile.get('description') != OLD_DESCRIPTION or post.get('text') != old_text:
        raise ValueError('Bio or pinned introduction was independently changed; refusing to overwrite')
    new_record['createdAt'] = post['createdAt']
    rpc(pds, 'com.atproto.repo.putRecord',
        {**post_params, 'swapRecord': post_current['cid'], 'record': new_record}, token=token)
    profile['description'] = NEW_DESCRIPTION
    rpc(pds, 'com.atproto.repo.putRecord',
        {**profile_params, 'swapRecord': profile_current['cid'], 'record': profile}, token=token)
    verified_profile = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=profile_params)
    verified_post = rpc(pds, 'com.atproto.repo.getRecord', token=token, params=post_params)
    if (verified_profile['value'].get('description') != NEW_DESCRIPTION or
            verified_post['value'].get('text') != new_record['text']):
        raise ValueError('Migration verification failed')
    print('Verified ShowWorth bio and pinned introduction; URI and creation time preserved.')

if __name__ == '__main__':
    main()
