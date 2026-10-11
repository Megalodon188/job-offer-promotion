import datetime as dt
import json
from pathlib import Path
import unittest
from post import APIError, allowed_pds, make_record, publish, daily_rkey

class PromotionTests(unittest.TestCase):
    def test_daily_record_key(self):
        day = dt.date(2026, 10, 11)
        key = daily_rkey(day)
        self.assertRegex(key, r'^[234567abcdefghij][234567abcdefghijklmnopqrstuvwxyz]{12}$')
        alphabet = '234567abcdefghijklmnopqrstuvwxyz'
        decoded = 0
        for char in key:
            decoded = decoded * 32 + alphabet.index(char)
        self.assertEqual(decoded >> 10, (day - dt.date(1970,1,1)).days * 86_400_000_000)
        self.assertEqual(key, daily_rkey(day))
        self.assertNotEqual(key, daily_rkey(day + dt.timedelta(days=1)))
    def test_revision_campaign_and_isolation(self):
        day = dt.date(2026, 10, 11)
        self.assertNotEqual(daily_rkey(day,1022), daily_rkey(day))
        self.assertEqual(daily_rkey(day,1022), daily_rkey(day,1022))
        posts = json.loads(Path('revision_posts.json').read_text())
        self.assertEqual(len(posts),30)
        self.assertEqual(len(set(posts)),30)
        url = 'https://payhip.com/b/xWm6F'
        for text in posts:
            record = make_record(text,url,day,'Revision Desk (desktop)')
            self.assertIn('Revision Desk (desktop): '+url,record['text'])
            self.assertNotIn('$5 calculator',record['text'])
            offset = record['facets'][0]['index']
            self.assertEqual(record['text'].encode()[offset['byteStart']:offset['byteEnd']],url.encode())
    def test_hashtag_byte_offsets(self):
        record = make_record('café #VideoEditing #Freelance','https://payhip.com/b/xWm6F',dt.date(2026,10,11),'Revision Desk')
        tags = record['facets'][1:]
        self.assertEqual(len(tags),2)
        self.assertEqual(tags[0]['features'][0]['tag'],'VideoEditing')
        for facet in tags:
            i = facet['index']
            self.assertEqual(record['text'].encode()[i['byteStart']:i['byteEnd']],('#'+facet['features'][0]['tag']).encode())
    def test_demo_campaign_destination(self):
        url = 'https://revision-desk-demo.quietgrass17.chatgpt.site'
        for text in json.loads(Path('revision_posts.json').read_text()):
            record = make_record(text,url,dt.date(2026,10,11),'Free revision check')
            offset = record['facets'][0]['index']
            self.assertEqual(record['text'].encode()[offset['byteStart']:offset['byteEnd']],url.encode())
        for bad in [url+'.evil.example',url+'/unapproved',url+'?unapproved=1']:
            with self.assertRaises(ValueError):
                make_record('Test',bad,dt.date(2026,10,11))
    def test_every_post_and_link_offsets(self):
        posts = json.loads(Path('posts.json').read_text())
        self.assertEqual(len(posts), 30)
        self.assertEqual(len(set(posts)), 30)
        for text in posts + ['A cafe offer: café work']:
            record = make_record(text, 'https://payhip.com/b/Ab123', dt.date(2026, 10, 11))
            offset = record['facets'][0]['index']
            self.assertEqual(record['text'].encode()[offset['byteStart']:offset['byteEnd']], b'https://payhip.com/b/Ab123')
    def test_endpoint_and_url_validation(self):
        self.assertTrue(allowed_pds('https://test.host.bsky.network'))
        for host in ['http://bsky.social', 'https://bsky.social.evil.example', 'https://user@bsky.social', 'https://bsky.social/path']:
            self.assertFalse(allowed_pds(host))
        for url in ['http://payhip.com/b/test', 'https://example.com/b/test', 'https://payhip.com/store']:
            with self.assertRaises(ValueError):
                make_record('Test', url, dt.date(2026, 10, 11))
    def test_create_and_duplicate_prevention(self):
        calls=[]
        session={'did':'did:plc:test','accessJwt':'test-access','didDoc':{'service':[{'type':'AtprotoPersonalDataServer','serviceEndpoint':'https://test.host.bsky.network'}]}}
        def fake(host, method, data=None, token=None, params=None):
            calls.append((host,method,data,params))
            if method.endswith('createSession'):
                return session
            if method.endswith('getRecord'):
                raise APIError(400,'RecordNotFound')
            return {'uri':'at://did:plc:test/app.bsky.feed.post/joboffer-20261011-1'}
        record=make_record('Test','https://payhip.com/b/Ab123',dt.date(2026,10,11))
        self.assertTrue(publish(record,'joboffer-20261011-1',' user.bsky.social ',' ab12-cd34-ef56-gh78 ',api=fake).startswith('Published'))
        self.assertEqual(calls[0][2], {'identifier':'user.bsky.social','password':'ab12-cd34-ef56-gh78'})
        self.assertEqual(calls[-1][2]['rkey'],'joboffer-20261011-1')
        self.assertEqual(calls[-1][0],'https://test.host.bsky.network')
        def existing(host, method, data=None, **kwargs):
            self.assertFalse(method.endswith('createRecord'))
            return session if method.endswith('createSession') else {'uri':'exists'}
        self.assertIn('No duplicate',publish(record,'same','user.bsky.social','aaaa-bbbb-cccc-dddd',api=existing))
    def test_unexpected_error_stops(self):
        def failed(host,method,data=None,**kwargs):
            if method.endswith('createSession'):
                return {'did':'did:plc:test','accessJwt':'test'}
            raise APIError(429,'RateLimitExceeded')
        with self.assertRaises(APIError):
            publish({},'key','user.bsky.social','aaaa-bbbb-cccc-dddd',api=failed)

if __name__=='__main__':
    unittest.main()
