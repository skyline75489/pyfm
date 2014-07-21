#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

class Douban:
    """ Douban class, provides some APIs.
    """
    def __init__(self):
        self.login_url = 'http://www.douban.com/j/app/login'
        self.channel_url = 'http://www.douban.com/j/app/radio/channels'
        self.api_url = 'http://www.douban.com/j/app/radio/people'
        self.app_name = 'radio_desktop_win'
        self.version = '100'
        self.typeMap = {
            'new': 'n',
            'playing': 'p',
            'rate': 'r',
            'unrate': 'u'
            'end': 'e',
            'bye': 'b',
            'skip': 's',
        }
        
        self.email = None
        self.password = None
        
        self.user_id = None
        self.expire = None
        self.token = None
        self.user_name = None
        
        self.channels = None
        self._load_config()

    def _load_config(self):
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            
            self.email = config['email']
            self.password = config['password']
        except (IOError, KeyError):
            raise Exception("Config not found")
        
        try:
            self.user_name = config['user_name']
            self.user_id = config['user_id']
            self.expire = config['expire']
            self.token = config['token']
        except KeyError:
            r = self._do_login()
            if r:
                self._save_config()
         
    def _save_config(self):
        f = None
        try:
            f = open('config.json', 'w')
            json.dump({
                'email': self.email,
                'password': self.password,
                'user_name': self.user_name,
                'user_id': self.user_id,
                'expire': self.expire,
                'token': self.token
            }, f)
        except IOError:
            raise Exception("Unable to write config file")
    
    def _do_api_request(self, sid=None, channel=None, kbps=64, _type):
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id, 
                'expire': self.expire, 'token': self.token, 'sid': sid, 'h': '','channel': channel, 'type': _type}
        
        r = requests.get(self.api_url, params=payload)
        return r
        
    def _do_login(self):
        payload = {'email': self.email, 'password': self.password, 'app_name': self.app_name, 'version': self.version}
        r = requests.post(self.login_url, params=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if r.json()['r'] == 0:
            self.user_name = r.json()['user_name']
            self.user_id = r.json()['user_id']
            self.expire = r.json()['expire']
            self.token = r.json()['token']
            return True
        else:
            return False
            
    def _get_type(self, option):
        return self.typeMap[option]
        
    def get_channels(self):
        """ Return a list of channels
        """
        if self.channels is None:
            r = requests.get(self.channel_url)
            # Cache channels
            self.channels = r.json()['channels']
            return self.channels
        return self.channels

    def get_new_play_list(self, channel, kbps=64):
        _type = self._get_type('new')
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id, 
                'expire': self.expire, 'token': self.token, 'sid': '', 'h': '','channel': channel, 'kbps': kbps, 'type': _type}
        
        r = requests.get(self.api_url, params=payload)
        if r.json()['r'] == 0:
            songs = r.json()['song']
            return songs
            
    def get_playing_list(self, sid, channel, kbps=64):
        _type = self._get_type('playing')
        payload = {'app_name': self.app_name, 'version': self.version, 'user_id': self.user_id, 
                'expire': self.expire, 'token': self.token, 'sid': sid, 'h': '','channel': channel, 'kbps': kbps, 'type': _type}
        
        r = requests.get(self.api_url, params=payload)
        if r.json()['r'] == 0:
            songs = r.json()['song']
            return songs

    def rate_song(self, sid, channel):
        _type = self._get_type('rate')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        return r
    
    def unrate_song(self, sid, channel):
        _type = self._get_type('unrate')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        return r
        
    def skip_song(self, sid, channel):
        _type = self._get_type('skip')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        return r
        
    def end_song(self, sid, channel):
        _type = self._get_type('end')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        return r
        
    def bye_song(self, sid, channel):
        _type = self._get_type('bye')
        r = self._do_api_request(sid=sid, channel=channel, _type=_type)
        return r
        
        