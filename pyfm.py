# /usr/bin/env python3
import os
import sys
import subprocess
import time
from collections import deque

from douban import Douban
from song import Song
from player import Player

class Pyfm:
    def __init__(self):
        self.douban = Douban()
        self.player = Player()
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None
        
    def _list_channels(self):
        channels = self.douban.get_channels()
        for channel in channels:
            print(str(channel['seq_id']) + " " + str(channel['name']))
    
    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(self.douban.get_new_play_list(self.current_channel))
        
    def _play(self):
        while True:
            _song = self.current_song_list.popleft()                
            self.current_song = Song(_song)
            
            # Currently playing the last song in queue
            if len(self.current_play_list) == 0:
                # Extend playlist
                playing_list = self.douban.get_playing_list(self.current_song.sid, self.current_channel)
                self.current_song_list.extend(deque(playing_list))
                
            self.player.play(self.current_song)
            # player process exit unsucessful
            if self.player.return_code != 0:
                print("Something wrong happens while playing...")
                return 
                
            self.player.bye_song(self.current_song.sid, self.current_channel)
            
    def start(self):
        # self._list_channels()
        self._choose_channel(2)
        self._play()
        
        
if __name__ == "__main__":
    fm = Pyfm()
    fm.start()
