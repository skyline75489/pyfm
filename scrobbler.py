### Scrobbler protocol v1.2
### See http://www.audioscrobbler.net/development/protocol/
from hashlib import md5
from time import time

import requests

debug = False

def logger(message):
    if debug:
        print('[Scrobbler]' + message)
        
class Scrobbler():

    # client : 3 chars
    # DEPRECATED : tst 1.0 - lastfm clientId for dev. Lastfm threats to disable it for version 1.2 http://www.last.fm/api/submissions
    # So, now use the client id of mpdscribble : mdc 0.22 http://git.musicpd.org/cgit/master/mpdscribble.git/tree/src/scrobbler.c#n45
    def __init__(self, user, password, client="mdc", version="0.22"):
        self.url      = "http://post.audioscrobbler.com/"
        self.user     = user
        self.password = password
        self.client   = client
        self.version  = version

    def handshake(self):
        logger('handshake')
        timestamp = int(time()).__str__()
        logger(timestamp)
        
        password = self.password.encode('utf-8')
        inner_md5 = (md5(password).hexdigest() + timestamp).encode('utf-8')
        auth = md5(inner_md5).hexdigest()
        logger(auth)

        payload = {
            "hs" : "true",
            "p"  : "1.2",
            "c"  : self.client,
            "v"  : self.version,
            "u"  : self.user,
            "t"  : timestamp,
            "a"  : auth
        }
        
        r = requests.get(self.url, params=payload)        
        resp = r.text
        
        if resp.startswith("BADUSER"):
            logger('BADUSER')
            return False

        if resp.startswith("UPTODATE"):
            logger('UPTODATE')
            return False

        if resp.startswith("FAILED"):
            logger('FAILED')
            return False

        if resp.startswith("BADAUTH"):
            logger('BADAUTH')
            return False
            
        resp_info = resp.split("\n") 
        self.session_id      = resp_info[1].rstrip()
        self.now_playing_url = resp_info[2].rstrip()
        self.submission_url  = resp_info[3].rstrip()

        return True

    def now_playing(self, artist, title, album="", length="", tracknumber="", mb_trackid=""):
        logger("Now playing %s - %s - %s" %(artist, title, album))
        
        payload = {
            "s": self.session_id,
            "a": artist,
            "t": title,
            "b": album,
            "l": length,
            "n": tracknumber,
            "m": mb_trackid
        }
        
        r = requests.post(self.now_playing_url, params=payload)
        resp = r.text

        if resp.startswith("OK"):
            logger('Now playing OK')
            return True

        if resp.startswith("FAILED"):
            logger('Now playing FAILED')
            return False

    def submit(self, artist, title, album="", length="", tracknumber="", mb_trackid=""):
        logger("Submitting %s - %s" %(artist, title))

        timestamp = int(time())
        
        payload = {
            "s": self.session_id,
            "a[0]": artist,
            "t[0]": title,
            "i[0]": timestamp-length,
            "o[0]": "R",
            "r[0]": "",
            "l[0]": length,
            "b[0]": album,
            "n[0]": tracknumber,
            "m[0]": mb_trackid
        }
        
        r = requests.post(self.submission_url, params=payload)
        resp = r.text

        if resp.startswith("OK"):
            logger("Submitting OK")
            return True

        if resp.startswith("FAILED"):
            logger("Submitting FAILED")
            return False
