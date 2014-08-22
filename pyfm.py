#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
from collections import deque
import logging

import urwid

from douban import Douban
from song import Song
from player import Player
from scrobbler import Scrobbler

logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    filename='fm.log', 
                    level=logging.DEBUG)

logger = logging.getLogger('main')

class Doubanfm:

    def __init__(self):
        # config and tools
        self._load_config()
        self.douban = Douban(
            self.email, self.password, self.user_id, self.expire, self.token, self.user_name)
        self.player = Player()
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None

        # terminal ui
        self.palette = [('selected', 'bold', 'default'),
                        ('title', 'yellow', 'default')]
        self.selected_button = None
        self.main_loop = None
        self.song_change_alarm = None

        if self.scrobbling:
            self.scrobbler = Scrobbler(
                self.last_fm_username, self.last_fm_password)
            r = self.scrobbler.handshake()
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
        self.get_channels()

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

        except (KeyError, ValueError):
            self.douban_account = False
            print("Douban account not found. Personal FM disabled.")

        try:
            if config == None:
                raise ValueError
            self.last_fm_username = config['last_fm_username']
            self.last_fm_password = config['last_fm_password']
        except (KeyError, ValueError):
            self.scrobbling = False
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
            self.channels = deque(self.douban.get_channels())
        # Not logged in. Disable personal radio
        if not self.douban_account:
            self.channels.popleft()
        return self.channels

    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(
            self.douban.get_new_play_list(self.current_channel))

    def _play_track(self):
        _song = self.current_play_list.popleft()
        self.current_song = Song(_song)
        logger.debug("Current Song: "+self.current_song.artist+' - '+self.current_song.song_title+ ' - '+self.current_song.album_title)
        
        self.song_change_alarm = self.main_loop.set_alarm_in(self.current_song.length_in_sec,
                                                             self.next_song, None)
        self.selected_button.set_text(self.selected_button.text[0:7].strip())
        heart = u'\N{WHITE HEART SUIT}'
        if self.current_song.like:
            heart = u'\N{BLACK HEART SUIT}'
        if not self.douban_account:
            heart = ' '
        self.selected_button.set_text(self.selected_button.text + '                 ' + heart + '  ' +
                                      self.current_song.artist + ' - ' +
                                      self.current_song.song_title)
        if self.scrobbling:
            self.scrobbler.now_playing(self.current_song.artist, self.current_song.song_title,
                                       self.current_song.album_title, self.current_song.length_in_sec)

        self.player.stop()
        self.player.play(self.current_song)
        # Currently playing the second last song in queue
        if len(self.current_play_list) == 1:
            # Extend the playing list
            playing_list = self.douban.get_playing_list(
                self.current_song.sid, self.current_channel)
            self.current_play_list.extend(deque(playing_list))

    def next_song(self, loop, user_data):
        # Scrobble the track if scrobbling is enabled
        # and total playback time of the track > 30s
        if self.scrobbling and self.current_song.length_in_sec > 30:
            self.scrobbler.submit(self.current_song.artist, self.current_song.song_title,
                                  self.current_song.album_title, self.current_song.length_in_sec)

        self.douban.end_song(self.current_song.sid, self.current_channel)
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()

    def skip_current_song(self):
        self.douban.skip_song(self.current_song.sid, self.current_channel)
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()

    def rate_current_song(self):
        if not self.douban_account:
            return
        r, err = self.douban.rate_song(
            self.current_song.sid, self.current_channel)
        if r:
            self.current_song.like = True
            self.selected_button.set_text(self.selected_button.text.replace(
                u'\N{WHITE HEART SUIT}', u'\N{BLACK HEART SUIT}'))
        else:
            logger.error(err)

    def unrate_current_song(self):
        if not self.douban_account:
            return
        r, err = self.douban.unrate_song(
            self.current_song.sid, self.current_channel)
        if r:
            self.current_song.like = False
            self.selected_button.set_text(self.selected_button.text.replace(
                u'\N{BLACK HEART SUIT}', u'\N{WHITE HEART SUIT}'))
        else:
            logger.error(err)

    def trash_current_song(self):
        if not self.douban_account:
            return
        r, err = self.douban.bye_song(
            self.current_song.sid, self.current_channel)
        if r:
            # play next song
            if self.song_change_alarm:
                self.main_loop.remove_alarm(self.song_change_alarm)
            self._play_track()
        else:
            logger.error(err)

    def quit(self):
        self.player.stop()

    def start(self):
        title = urwid.AttrMap(urwid.Text('豆瓣FM'), 'title')
        divider = urwid.Divider()
        pile = urwid.Padding(
            urwid.Pile([divider, title, divider]), left=4, right=4)
        box = urwid.Padding(self.ChannelListBox(), left=2, right=4)

        frame = urwid.Frame(box, header=pile, footer=divider)

        self.main_loop = urwid.MainLoop(
            frame, self.palette, handle_mouse=False)
        self.main_loop.run()

    def ChannelListBox(self):
        body = []
        for c in self.channels:
            _channel = ChannelButton(c['name'])
            urwid.connect_signal(
                _channel, 'click', self.channel_chosen, c['channel_id'])
            body.append(urwid.AttrMap(_channel, None, focus_map="channel"))
        return MyListBox(urwid.SimpleFocusListWalker(body), self)

    def channel_chosen(self, button, choice):
        # Choose the channel which is playing right now
        # ignore this
        if self.selected_button == button:
            return
        # Choose a different channel
        if self.player.is_playing:
            self.player.stop()
        self._choose_channel(choice)
        if self.selected_button != None and button != self.selected_button:
            self.selected_button.set_text(
                self.selected_button.text[0:7].strip())
        self.selected_button = button
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()


class ChannelButton(urwid.Button):

    def __init__(self, caption):
        super(ChannelButton, self).__init__("")
        self._text = urwid.SelectableIcon([u'\N{BULLET} ', caption], 0)
        self._w = urwid.AttrMap(self._text, None, focus_map='selected')

    @property
    def text(self):
        return self._text.text

    def set_text(self, text):
        self._text.set_text(text)


class MyListBox(urwid.ListBox):

    def __init__(self, body, fm):
        super(MyListBox, self).__init__(body)
        self.fm = fm

    def keypress(self, size, key):
        if key in ('up', 'down', 'page up', 'page down', 'enter'):
            return super(MyListBox, self).keypress(size, key)
        if key == ('j'):
            return super(MyListBox, self).keypress(size, 'down')
        if key == ('k'):
            return super(MyListBox, self).keypress(size, 'up')
        if key in ('q', 'Q'):
            self.fm.quit()
            raise urwid.ExitMainLoop()
        if key == ('n'):
            self.fm.skip_current_song()
        if key == ('l'):
            if self.fm.current_song.like:
                self.fm.unrate_current_song()
            else:
                self.fm.rate_current_song()
        if key == ('t'):
            self.fm.trash_current_song()


if __name__ == "__main__":
    fm = Doubanfm()
    fm.start()
