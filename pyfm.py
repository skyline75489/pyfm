#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import subprocess
import time
import json
import logging

from hashlib import md5
from collections import deque
from getpass import getpass

import urwid

from douban import Douban
from song import Song
from player import Player
from scrobbler import Scrobbler
from notifier import Notifier

logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s %(message)s',
                    filename='fm.log',
                    level=logging.DEBUG)

logger = logging.getLogger()


class Doubanfm(object):

    def __init__(self):
        self.email = None
        self.password = None
        self.user_name = None
        self.user_id = None
        self.expire = None
        self.token = None
        self.cookies = None

        self.last_fm_username = None
        self.last_fm_password = None
        self.scrobbling = True
        self.douban_account = True
        self.channels = None

        # Set up config
        try:
            arg = sys.argv[1]
            self._do_config()
        except IndexError:
            self._load_config()

        # Init API tools
        self.douban = Douban(
            self.email, self.password, self.user_id, self.expire, self.token, self.user_name, self.cookies)
        self.player = Player()
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None

        # Init terminal ui
        self.palette = [('selected', 'bold', 'default'),
                        ('title', 'yellow', 'default')]
        self.selected_button = None
        self.main_loop = None
        self.song_change_alarm = None

        # Try to login
        if self.last_fm_username is None or self.last_fm_username == "":
            self.scrobbling = False
        if (self.email is None or self.email == "") and self.cookies == None:
            self.douban_account = False

        if self.scrobbling:
            self.scrobbler = Scrobbler(
                self.last_fm_username, self.last_fm_password)
            r, err = self.scrobbler.handshake()
            if r:
                print("Last.FM 已登陆")
            else:
                print("Last.FM 登录失败: " + err)
        if self.douban_account:
            r, err = self.douban.do_login()
            if r:
                print("Douban 已登陆")
            else:
                print("Douban 登录失败: " + err)
        self.get_channels()
        self._save_cache()

    def _do_config(self):
        self.email = input('豆瓣账户 (Email地址): ') or None
        self.password = getpass('豆瓣密码: ') or None
        self.last_fm_username = input('Last.fm 用户名: ') or None
        password = getpass('Last.fm 密码: ') or None
        self.last_fm_password = md5(password.encode('utf-8')).hexdigest()

    def _load_config(self):
        try:
            f = open('channels.json', 'r')
            self.channels = deque(json.load(f))
            logger.debug("Load channel file.")
        except FileNotFoundError:
            logger.debug("Channels file not found.")

        try:
            f = open('cache.json', 'r')
            cache = json.load(f)
            try:
                self.user_name = cache['user_name']
                self.user_id = cache['user_id']
                self.expire = cache['expire']
                self.token = cache['token']
                self.cookies = cache['cookies']
            except (KeyError, ValueError):
                self.douban_account = False
            try:
                self.last_fm_username = cache['last_fm_username']
                self.last_fm_password = cache['last_fm_password']
            except (KeyError, ValueError):
                self.scrobbling = False

        except FileNotFoundError:
            logger.debug("Cache file not found.")

    def _save_cache(self):
        f = None
        try:
            f = open('cache.json', 'w')
            f2 = open('channels.json', 'w')
            json.dump({
                'user_name': self.douban.user_name,
                'user_id': self.douban.user_id,
                'expire': self.douban.expire,
                'token': self.douban.token,
                'cookies': self.douban.cookies,
                'last_fm_username': self.last_fm_username,
                'last_fm_password': self.last_fm_password
            }, f)
            json.dump(list(self.channels), f2)
        except IOError:
            raise Exception("Unable to write cache file")

    def get_channels(self):
        if self.channels is None:
            self.channels = deque(self.douban.get_channels())

    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(
            self.douban.get_new_play_list(self.current_channel))

    def _play_track(self):
        _song = self.current_play_list.popleft()
        self.current_song = Song(_song)
        logger.debug('Playing Track')
        logger.debug('Artist: ' + self.current_song.artist)
        logger.debug('Title: ' + self.current_song.song_title)
        logger.debug('Album: ' + self.current_song.album_title)
        logger.debug('Length: ' + self.current_song.length_in_str)
        logger.debug('Sid: ' + self.current_song.sid)

        # Post notification
        Notifier.notify("", self.current_song.song_title, self.current_song.artist + ' — ' +
                        self.current_song.album_title, appIcon=self.current_song.picture, open_URL=self.current_song.album)
        logger.debug(
            '{0} tracks remaining in the playlist'.format(len(self.current_play_list)))

        self.song_change_alarm = self.main_loop.set_alarm_in(self.current_song.length_in_sec,
                                                             self.next_song, None)
        self.selected_button.set_text(self.selected_button.text[0:11].strip())
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
            logger.debug('Got {0} more tracks'.format(len(playing_list)))
            self.current_play_list.extend(deque(playing_list))

    def next_song(self, loop, user_data):
        # Scrobble the track if scrobbling is enabled
        # and total playback time of the track > 30s
        if self.scrobbling and self.current_song.length_in_sec > 30:
            self.scrobbler.submit(self.current_song.artist, self.current_song.song_title,
                                  self.current_song.album_title, self.current_song.length_in_sec)

        if self.douban_account:
            r, err = self.douban.end_song(
                self.current_song.sid, self.current_channel)
            if r:
                logger.debug('End song OK')
            else:
                logger.error(err)
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()

    def skip_current_song(self):
        if self.douban_account:
            r, err = self.douban.skip_song(
                self.current_song.sid, self.current_channel)
            if r:
                logger.debug('Skip song OK')
            else:
                logger.error(err)
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
            logger.debug('Rate song OK')
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
            logger.debug('Unrate song OK')
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
            logger.debug('Trash song OK')
        else:
            logger.error(err)

    def quit(self):
        logger.debug('Quit')
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
                self.selected_button.text[0:11].strip())
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
