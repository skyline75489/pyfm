# -*- coding: utf-8 -*-
import requests
import json


class Douban:

    """ Douban class, provides some APIs.
    """

    def __init__(self, email, password, user_id=None, expire=None, token=None, user_name=None, cookies=None):
        self.login_url = 'https://www.douban.com/j/app/login'
        self.channel_url = 'https://www.douban.com/j/app/radio/channels'
        self.api_url = 'https://www.douban.com/j/app/radio/people'
        self.app_name = 'radio_desktop_win'
        self.version = '100'
        self.type_map = {
            'new': 'n',
            'playing': 'p',
            'rate': 'r',
            'unrate': 'u',
            'end': 'e',
            'bye': 'b',
            'skip': 's',
        }

        self.email = email
        self.password = password

        self.user_id = user_id
        self.expire = expire
        self.token = token
        self.user_name = user_name
        self.cookies = cookies
        
        self.logged_in = False
        self.channels = None

    def _do_api_request(self, _type, sid=None, channel=None, kbps=64):
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id,
                   'expire': self.expire, 'token': self.token, 'sid': sid, 'h': '', 'channel': channel, 'type': _type}

        r = requests.get(self.api_url, params=payload, cookies=self.cookies)
        return r

    def do_login(self):
        # Has cookies already. No need to login again.
        if self.cookies:
            self.logged_in = True
            return True, None
        payload = {'email': self.email, 'password': self.password,
                   'app_name': self.app_name, 'version': self.version}
        r = requests.post(self.login_url, params=payload, headers={
                          'Content-Type': 'application/x-www-form-urlencoded'})
        if r.json()['r'] == 0:
            self.user_name = r.json()['user_name']
            self.user_id = r.json()['user_id']
            self.expire = r.json()['expire']
            self.token = r.json()['token']
            self.cookies = r.cookies.get_dict()
            self.logged_in = True
            return True, None
        else:
            return False, r.json()['err']

    def _get_type(self, option):
        return self.type_map[option]

    def get_channels(self):
        """ Return a list of channels
        """
        if self.channels is None:
            r = requests.get(self.channel_url)
            # Cache channels
            channels = r.json()['channels']
            if self.logged_in:
                # No api for this. 
                # We have to manually add this.
                heart = {u'seq_id': -3, 
                        u'name_en': u'Heart', 
                        u'abbr_en': u'Heart', 
                        u'name': u'红心兆赫', 
                        u'channel_id': -3}
                channels.insert(0, heart)
            self.channels = channels
            return self.channels
        else:
            return self.channels

    def get_new_play_list(self, channel, kbps=64):
        _type = self._get_type('new')
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id,
                   'expire': self.expire, 'token': self.token, 'sid': '', 'h': '', 'channel': channel, 'kbps': kbps, 'type': _type}

        r = requests.get(self.api_url, params=payload)
        if r.json()['r'] == 0:
            songs = r.json()['song']
            return songs

    def get_playing_list(self, sid, channel, kbps=64):
        _type = self._get_type('playing')
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id,
                   'expire': self.expire, 'token': self.token, 'sid': sid, 'h': '', 'channel': channel, 'kbps': kbps, 'type': _type}

        r = requests.get(self.api_url, params=payload)
        if r.json()['r'] == 0:
            songs = r.json()['song']
            return songs

    def rate_song(self, sid, channel):
        _type = self._get_type('rate')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        if r.json()['r'] == 0:
            return True, None
        else:
            return False, r.json()['err']

    def unrate_song(self, sid, channel):
        _type = self._get_type('unrate')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        if r.json()['r'] == 0:
            return True, None
        else:
            return False, r.json()['err']

    def skip_song(self, sid, channel):
        _type = self._get_type('skip')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        if r.json()['r'] == 0:
            return True, None
        else:
            return False, r.json()['err']

    def end_song(self, sid, channel):
        _type = self._get_type('end')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        if r.json()['r'] == 0:
            return True, None
        else:
            return False, r.json()['err']

    def bye_song(self, sid, channel):
        """No longer play this song
        """
        _type = self._get_type('bye')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        if r.json()['r'] == 0:
            return True, None
        else:
            return False, r.json()['err']
