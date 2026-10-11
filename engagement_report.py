"""Read-only public engagement report. Does not infer sales or impressions."""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ACTOR='did:plc:rmvvl2twnwbculbftv6aebv6'
DEMO='https://revision-desk-demo.quietgrass17.chatgpt.site'

def api(method,**params):
    url='https://public.api.bsky.app/xrpc/'+method+'?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'RevisionDeskEngagement/1.0'}),timeout=30) as response:
        return json.load(response)

def main():
    today=dt.datetime.now(dt.timezone.utc).date()
    if today>dt.date(2026,11,10):
        print('Reporting window finished.')
        return
    profile=api('app.bsky.actor.getProfile',actor=ACTOR)
    feed=api('app.bsky.feed.getAuthorFeed',actor=ACTOR,limit=100,filter='posts_no_replies')
    posts=[]
    for item in feed.get('feed',[]):
        p=item['post']
        if p['author']['did']!=ACTOR:
            continue
        text=p.get('record',{}).get('text','')
        if 'Revision Desk' in text or DEMO in text or 'https://payhip.com/b/xWm6F' in text:
            posts.append(p)
    followers=profile.get('followersCount',0)
    interactions=sum(p.get(k,0) for p in posts for k in ['likeCount','repostCount','replyCount'])
    lines=['# Revision Desk engagement — '+today.isoformat()+' UTC','',
           '- Followers: '+str(followers),'- Relevant original posts in the latest 100 feed items: '+str(len(posts)),
           '- Likes: '+str(sum(p.get('likeCount',0) for p in posts)),
           '- Reposts: '+str(sum(p.get('repostCount',0) for p in posts)),
           '- Replies: '+str(sum(p.get('replyCount',0) for p in posts)),
           '', '**Not available here:** post impressions, unique demo visitors, checkout clicks, purchases, refunds or profit.',
           'Public engagement is not buyer validation. These totals are current snapshots, not daily changes.','']
    if followers==0 and interactions==0:
        lines.append('**Priority: distribution.** No followers or visible engagement yet. Do not interpret more scheduled posts as proof of demand.')
    else:
        lines.append('**Priority: inspect the strongest posts and obtain actual checkout/sales evidence in Payhip.** Likes and replies do not establish conversion.')
    lines.extend(['','| Post | Likes | Reposts | Replies |','|---|---:|---:|---:|'])
    for p in sorted(posts,key=lambda x:sum(x.get(k,0) for k in ['likeCount','repostCount','replyCount']),reverse=True)[:10]:
        key=p['uri'].rsplit('/',1)[1]
        link='https://bsky.app/profile/'+ACTOR+'/post/'+key
        lines.append('| [Open post]('+link+') | '+str(p.get('likeCount',0))+' | '+str(p.get('repostCount',0))+' | '+str(p.get('replyCount',0))+' |')
    result='\n'.join(lines)+'\n'
    print(result)
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as output:
            output.write(result)

if __name__=='__main__':
    main()
