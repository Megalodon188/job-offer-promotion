"""One-time, idempotent introduction and empty-profile setup for our own account."""
import argparse
import datetime as dt
import os
from post import APIError, allowed_pds, daily_rkey, make_record, publish, rpc

DEMO = 'https://revision-desk-demo.quietgrass17.chatgpt.site'
EXPECTED_DID = 'did:plc:rmvvl2twnwbculbftv6aebv6'
LAUNCH_DAY = dt.date(2026, 10, 11)
BODY = ('Fixed-price video editors: try this free revision-cost check. Enter your price and hours to see how extra time changes your effective pay. No email gate. Full paid tool is optional. #VideoEditing #Freelance')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    record = make_record(BODY, DEMO, LAUNCH_DAY, 'Free tool')
    if args.dry_run:
        print(record['text'])
        return
    if dt.datetime.now(dt.timezone.utc).date() != LAUNCH_DAY:
        print('One-time launch window closed; no changes made.')
        return
    handle = os.environ['BSKY_HANDLE'].strip()
    password = os.environ['BSKY_APP_PASSWORD'].strip()
    session = rpc('https://bsky.social', 'com.atproto.server.createSession', {'identifier':handle.lstrip('@'), 'password':password})
    if session['did'] != EXPECTED_DID:
        raise ValueError('Connected account does not match the intended promotion account.')
    pds = 'https://bsky.social'
    for service in session.get('didDoc',{}).get('service',[]):
        if service.get('type') == 'AtprotoPersonalDataServer':
            pds = service['serviceEndpoint'].rstrip('/')
    if not allowed_pds(pds):
        raise ValueError('Unexpected account server.')
    token = session['accessJwt']
    record['createdAt'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
    rkey = daily_rkey(LAUNCH_DAY,1021)
    print(publish(record,rkey,handle,password))
    posted = rpc(pds,'com.atproto.repo.getRecord',token=token,params={'repo':EXPECTED_DID,'collection':'app.bsky.feed.post','rkey':rkey})
    params = {'repo':EXPECTED_DID,'collection':'app.bsky.actor.profile','rkey':'self'}
    try:
        current = rpc(pds,'com.atproto.repo.getRecord',token=token,params=params)
        profile = dict(current['value'])
        swap = {'swapRecord':current['cid']}
    except APIError as exc:
        if exc.code != 'RecordNotFound':
            raise
        profile = {'$type':'app.bsky.actor.profile'}
        swap = {'swapRecord':None}
    changed = False
    if not profile.get('displayName'):
        profile['displayName'] = 'Revision Desk | Practical Tools'
        changed = True
    if not profile.get('description'):
        profile['description'] = 'Practical tools for work and freelance editing. Free revision-cost check: '+DEMO+' | Paid downloads on Payhip. Automated product updates.'
        changed = True
    if not profile.get('pinnedPost'):
        profile['pinnedPost'] = {'uri':posted['uri'],'cid':posted['cid']}
        changed = True
    if changed:
        rpc(pds,'com.atproto.repo.putRecord',{**params,**swap,'record':profile},token=token)
        print('Filled empty profile fields and pinned the demo introduction.')
    else:
        print('Existing profile fields and pin preserved.')
    print('Post: https://bsky.app/profile/'+EXPECTED_DID+'/post/'+rkey)

if __name__ == '__main__':
    main()
