# /usr/bin/env python3
import os
import sys
import subprocess
import time
import json
from collections import deque

from douban import Douban
from song import Song
from player import Player
from scrobbler import Scrobbler

class Pyfm:
    def __init__(self):
        self._load_config()
        self.douban = Douban(self.email, self.password, self.user_id, self.expire, self.token, self.user_name)
        self.player = Player()
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None
        
        if self.scrobbling:
            self.scrobbler = Scrobbler(self.last_fm_username, self.last_fm_password)
            r =  self.scrobbler.handshake()
            if r:
                print("Last.FM Logged in.")
        if self.douban_account:
            r = self.douban.do_login()
            if r:
                print("Douban Logged in.")
        
    def _load_config(self):
        self.email = None
        self.password = None
        self.user_id = None
        self.expire = None
        self.token = None
        self.user_name = None
        self.lasf_fm_username = None
        self.last_fm_password = None
        self.scrobbling = True
        self.douban_account = True
        
        config = None
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            
            self.email = config['email']
            self.password = config['password']
            
        except KeyError:
            self.douban_account = False
            print("Douban account not found. Personal FM disabled.")
        
        try: 
            self.last_fm_username = config['last_fm_username']
            self.last_fm_password = config['last_fm_password']
        except KeyError:
            self.scrobbing = False
            print("Last.fm account not found. Scrobbling disabled.")
         
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
                'token': self.token,
                'last_fm_username': self.last_fm_username,
                'last_fm_password': self.last_fm_password
            }, f)
        except IOError:
            raise Exception("Unable to write config file")
            
    def _list_channels(self):
        channels = self.douban.get_channels()
        for channel in channels:
            print(str(channel['seq_id']) + " " + str(channel['name']))
    
    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(self.douban.get_new_play_list(self.current_channel))
        
    def _play(self):
        while True:
            _song = self.current_play_list.popleft()                
            self.current_song = Song(_song)
            if self.scrobbling:
                self.scrobbler.now_playing(self.current_song.artist, self.current_song.title,
                                           self.current_song.album_title, self.current_song.length_in_sec)
            
            # Currently playing the last song in queue
            if len(self.current_play_list) == 0:
                # Extend playlist
                print("Extending playlist...")
                playing_list = self.douban.get_playing_list(self.current_song.sid, self.current_channel)
                self.current_play_list.extend(deque(playing_list))
                
            self.player.play(self.current_song)
            # player process exit unsucessful
            if self.player.return_code != 0:
                print("Something wrong happens while playing...")
                return 
                
            # Scrobble the track if scrobbling is enabled 
            # and total playback time of the track > 30s
            if self.scrobbling and self.current_song.length_in_sec > 30:
                self.scrobbler.submit(self.current_song.artist, self.current_song.title,
                                      self.current_song.album_title, self.current_song.length_in_sec)
                
            self.douban.end_song(self.current_song.sid, self.current_channel)
            
    def start(self):
        # self._list_channels()
        self._choose_channel(2)
        self._play()
        
        
if __name__ == "__main__":
    fm = Pyfm()
    fm.start()
