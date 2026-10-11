import datetime as dt
import json
from pathlib import Path
import unittest
from post import APIError, allowed_pds, make_record, publish

class PromotionTests(unittest.TestCase):
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
