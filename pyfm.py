# /usr/bin/env python3
import os
import subprocess
import sys
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
        self.current_song_list = None
        
    def _list_channels(self):
        channels = self.douban.get_channels()
        for channel in channels:
            print(str(channel['seq_id']) + " " + str(channel['name']))
    
    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_song_list = deque(self.douban.get_song_list(self.current_channel))
        
    def _play(self):
        while True:
            song = self.current_song_list.popleft()
            self.current_song = Song(song)
            self.player.play(self.current_song)
            # player process exit unsucessful
            if self.player.return_code != 0:
                print("Something wrong happens while playing...")
                return 
            self.current_song_list.append(self.douban.get_song_list(self.current_channel)[0])
            
    
    def start(self):
        # self._list_channels()
        self._choose_channel(2)
        self._play()
        
        
if __name__ == "__main__":
    fm = Pyfm()
    fm.start()
