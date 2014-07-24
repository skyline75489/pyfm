# /usr/bin/env python3
import os
import sys
import subprocess
import time
import json
from collections import deque

import urwid

from douban import Douban
from song import Song
from player import Player
from scrobbler import Scrobbler

class Doubanfm:
    def __init__(self):
        self._load_config()
        self.douban = Douban(self.email, self.password, self.user_id, self.expire, self.token, self.user_name)
        self.player = Player()
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None
        self.get_channels()
        
        self.ui_channel_list = [str(l['channel_id']) + ' ' + l['name'] for l in self.channels]
        self.palette = [('channel', 'default,bold', 'default')]
        self.selected_button = None
        self.main_loop = None
        
        if self.scrobbling:
            self.scrobbler = Scrobbler(self.last_fm_username, self.last_fm_password)
            r =  self.scrobbler.handshake()
            if r:
                print("Last.FM logged in.")
            else:
                print("Last.FM login failed")
        if self.douban_account:
            r, err = self.douban.do_login()
            if r:
                print("Douban logged in.")
                self._save_cache()
            else:
                print("Douban login failed: " + err)
        
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
        self.channels = None
        
        config = None
        token = None
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
            
        try:
            f = open('channels.json', 'r')
            self.channels = json.load(f)
            print("Load channel file.")
        except FileNotFoundError:
            print("Channels file not found.")
         
    def _save_cache(self):
        f = None
        try:
            f = open('cache.json', 'w')
            f2 = open('channels.json', 'w')
            json.dump({
                'user_name': self.douban.user_name,
                'user_id': self.douban.user_id,
                'expire': self.douban.expire,
                'token': self.douban.token
            }, f)
            json.dump(self.channels, f2)
        except IOError:
            raise Exception("Unable to write cache file")
            
    def get_channels(self):
        if self.channels is None:
            self.channels = self.douban.get_channels()
        return self.channels
    
    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(self.douban.get_new_play_list(self.current_channel))
        
    def _play_track(self):
        _song = self.current_play_list.popleft()                
        self.current_song = Song(_song)
        self.main_loop.set_alarm_in(self.current_song.length_in_sec,
                                   self.next_song, None);
        self.selected_button.set_label(self.selected_button.label[0:7].strip())
        self.selected_button.set_label(self.selected_button.label + '          '+
                                        self.current_song.artist + ' - ' + 
                                        self.current_song.title)
        if self.scrobbling:
            self.scrobbler.now_playing(self.current_song.artist, self.current_song.title,
                                       self.current_song.album_title, self.current_song.length_in_sec)
        
        # Currently playing the second last song in queue
        if len(self.current_play_list) == 1:
            playing_list = self.douban.get_playing_list(self.current_song.sid, self.current_channel)
            self.current_play_list.extend(deque(playing_list))
            
        self.player.play(self.current_song)
    
    def next_song(self, loop, user_data):
        self.player.stop()
        # Scrobble the track if scrobbling is enabled 
        # and total playback time of the track > 30s
        if self.scrobbling and self.current_song.length_in_sec > 30:
            self.scrobbler.submit(self.current_song.artist, self.current_song.title,
                                  self.current_song.album_title, self.current_song.length_in_sec)
        
        self.douban.end_song(self.current_song.sid, self.current_channel)
        self._play_track()
            
    def start(self):
        self.main_loop = urwid.MainLoop(self.ChannelListBox(self.ui_channel_list), self.palette, handle_mouse=False)
        self.main_loop.run()
    
    def channel(self, channel):
        return urwid.Button((channel))

    def ChannelListBox(self, channel_list):
        body = [urwid.Text('豆瓣FM'), urwid.Divider()]
        for c in channel_list:
                _channel = self.channel(c)
                urwid.connect_signal(_channel, 'click', self.channel_chosen, c)
                body.append(urwid.AttrMap(_channel, None, focus_map="channel"))
        return MyListBox(urwid.SimpleFocusListWalker(body))

    def channel_chosen(self, button, choice):
        # Choose the channel which is playing right now
        # ignore this
        if self.selected_button == button:
            return
        # Choose a different channel
        if self.player.is_playing:
            self.player.stop()
        self._choose_channel(int(choice[:2]))
        if self.selected_button != None and button != self.selected_button:
            self.selected_button.set_label(self.selected_button.label[0:7].strip())
        self.selected_button = button
        self._play_track()

class MyListBox(urwid.ListBox):
        def keypress(self, size, key):
                if key in ('up', 'down', 'page up' ,'page down', 'enter'):
                        return super(MyListBox, self).keypress(size, key)
                if key == ('j'):
                        return super(MyListBox, self).keypress(size, 'down')
                if key == ('k'):
                        return super(MyListBox, self).keypress(size, 'up')
                if key in ('q', 'Q'):
                        raise urwid.ExitMainLoop() 
                if key == ('f'):
                        # skip track
                        pass
                if key == ('r'):
                        # rate track
                        pass
    
                                             
if __name__ == "__main__":
    fm = Doubanfm()
    fm.start()
    