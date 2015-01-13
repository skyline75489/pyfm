#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import subprocess
import time
import json
import logging

from hashlib import md5
from collections import deque
from functools import wraps

import urwid

from .douban import Douban
from .song import Song
from .player import Player
from .scrobbler import Scrobbler
from .notifier import Notifier
from .config import Config
from .ui import ChannelButton, ChannelListBox

logger = logging.getLogger()


__version__ = '0.2.4'

WHITE_HEART = u'\N{WHITE HEART SUIT}'
BLACK_HEART = u'\N{BLACK HEART SUIT}'

HELP = """
pyfm 0.2.4   使用Python编写的豆瓣FM命令行播放器

更新或安装：
$ [sudo] pip install pyfm --upgrade

配置：
$ pyfm config

操作快捷键：
    [n]  ->  跳过当前歌曲
    [l]  ->  给当前歌曲添加红心或删除红心
    [t]  ->  不再播放当前歌曲
    [q]  ->  退出播放器
"""


class Doubanfm(object):

    def __init__(self):
        self.douban = None
        self.player = None
        self.config = None
        self.scrobbler = None

        self.channels = None
        self.current_channel = 0
        self.current_song = None
        self.current_play_list = None

        self._setup_config()
        self._setup_api_tools()
        self._setup_ui()
        self._setup_signals()

    def _setup_config(self):
        self.config = Config()
        # Set up config
        try:
            arg = sys.argv[1]
            if arg == 'config':
                self.config.do_config()
            elif arg in ['help', '-h', '--help']:
                print(HELP)
                raise SystemExit()
            else:
                raise SystemExit('Bad arguments. Try "help" for more info.')
        except IndexError:
            self.config.load_config()

    def _setup_api_tools(self):
        # Init API tools
        self.player = Player()
        self.douban = Douban(
            self.email, self.password, self.user_id, self.expire, self.token, self.user_name, self.cookies)

        if self.last_fm_username is None or self.last_fm_username == "":
            self.scrobbling = False
        if (self.email is None or self.email == "") and self.cookies == None:
            self.douban_account = False

        # Try to login
        if self.scrobbling:
            self.scrobbler = Scrobbler(
                self.last_fm_username, self.last_fm_password)
            r, err = self.scrobbler.handshake()
            if r:
                logger.debug("Last.fm logged in.")
            else:
                print("Last.FM 登录失败: " + err)
                self.scrobbling = False

        if self.douban_account:
            r, err = self.douban.do_login()
            if r:
                logger.debug("Douban logged in")
            else:
                print("Douban 登录失败: " + err)
                self.douban_account = False

        # Refresh account cache
        self.config.save_account_cache(self.douban.user_name, self.douban.user_id, self.douban.expire, self.douban.token, self.douban.cookies,
                                       self.last_fm_username, self.last_fm_password, self.enable_notify)

    def _setup_ui(self):
        # Init terminal UI
        self.palette = [('selected', 'bold', 'default'),
                        ('title', 'yellow', 'default')]
        self.selected_button = None
        self.main_loop = None
        self.song_change_alarm = None

        self.get_channels()

        title = '豆瓣FM' + ' ' * 32
        if self.douban_account:
            title += '豆瓣已登录'
        else:
            title += '豆瓣未登陆'
        title += ' ' * 3
        if self.scrobbling:
            title += 'Last.fm 已登录'
        else:
            title += 'Last.fm 未登录'

        self.title = urwid.AttrMap(urwid.Text(title), 'title')
        self.divider = urwid.Divider()
        self.pile = urwid.Padding(
            urwid.Pile([self.divider, self.title, self.divider]), left=4, right=4)
        self.channel_list_box = self.getChannelListBox()
        self.box = urwid.Padding(self.channel_list_box, left=2, right=4)

        self.frame = urwid.Frame(
            self.box, header=self.pile, footer=self.divider)

        self.main_loop = urwid.MainLoop(
            self.frame, self.palette, handle_mouse=False)

        # Cache the channel list
        self.config.save_channel_cache(self.channels)

    def _setup_signals(self):
        urwid.register_signal(
            ChannelListBox, ['exit', 'skip', 'rate', 'trash'])

        urwid.connect_signal(self.channel_list_box, 'exit', self.on_exit)
        urwid.connect_signal(self.channel_list_box, 'skip', self.on_skip)
        urwid.connect_signal(
            self.channel_list_box, 'rate', self.on_rate_and_unrate)
        urwid.connect_signal(self.channel_list_box, 'trash', self.on_trash)

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            # Combine self.config.__dict__ and self.config.__dict__ for convenience
            return self.config.__dict__[name]

    # Some useful decorators
    def current_song_required(f):
        @wraps(f)
        def wrapper(self, *args, **kwds):
            if self.current_song is None:
                return
            return f(self, *args, **kwds)
        return wrapper

    def last_fm_account_required(f):
        @wraps(f)
        def wrapper(self, *args, **kwds):
            if not self.scrobbling:
                return
            return f(self, *args, **kwds)
        return wrapper

    def douban_account_required(f):
        @wraps(f)
        def wrapper(self, *args, **kwds):
            if not self.douban_account:
                return
            return f(self, *args, **kwds)
        return wrapper

    def get_channels(self):
        if self.channels is None:
            try:
                self.channels = self.cached_channels
            except KeyError:
                self.channels = deque(self.douban.get_channels())

    def _choose_channel(self, channel):
        self.current_channel = channel
        self.current_play_list = deque(
            self.douban.get_new_play_list(self.current_channel))

    def extend_playlist_if_needed(self):
        count_of_remaining_songs = len(self.current_play_list)
        logger.debug(
            '{0} tracks remaining in the playlist'.format(count_of_remaining_songs))
        if count_of_remaining_songs == 1:
            # There is only one track remaining in queue, extend the playing list
            playing_list = self.douban.get_playing_list(
                self.current_song.sid, self.current_channel)
            logger.debug('Got {0} more tracks'.format(len(playing_list)))
            self.current_play_list.extend(deque(playing_list))

    def _play_track(self):
        _song = self.current_play_list.popleft()
        self.current_song = Song(_song)

        self.notify_now_playing()
        self.song_change_alarm = self.main_loop.set_alarm_in(self.current_song.length_in_sec,
                                                             self.next_song, None)
        self.update_ui_for_now_playing()
        self.scrobble_now_playing()
        # Stop current song if any song is playing
        self.player.stop()  
        self.player.play(self.current_song)
        self.extend_playlist_if_needed()

    def update_ui_for_now_playing(self):
        self.selected_button.set_text(self.selected_button.text[0:11].strip())
        heart = WHITE_HEART
        if self.current_song.like:
            heart = BLACK_HEART
        if not self.douban_account:
            heart = ' '
        self.selected_button.set_text(self.selected_button.text + '                 ' + heart + '  ' +
                                      self.current_song.artist + ' - ' +
                                      self.current_song.song_title)

    def notify_now_playing(self):
        if self.enable_notify:
            Notifier.notify("", self.current_song.song_title, self.current_song.artist + ' — ' +
                            self.current_song.album_title, appIcon=self.current_song.picture, open_URL=self.current_song.album)

    def next_song(self, loop, user_data):
        self.submit_current_song()
        self.end_current_song
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()

    @last_fm_account_required
    def submit_current_song(self):
        # Submit the track if total playback time of the track > 30s
        if self.current_song.length_in_sec > 30:
            self.scrobbler.submit(self.current_song.artist, self.current_song.song_title,
                                  self.current_song.album_title, self.current_song.length_in_sec)

    @last_fm_account_required
    def scrobble_now_playing(self):
        self.scrobbler.now_playing(self.current_song.artist, self.current_song.song_title,
                                   self.current_song.album_title, self.current_song.length_in_sec)

    @current_song_required
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

    @current_song_required
    @douban_account_required
    def rate_current_song(self):
        r, err = self.douban.rate_song(
            self.current_song.sid, self.current_channel)
        if r:
            self.current_song.like = True
            self.selected_button.set_text(self.selected_button.text.replace(
                WHITE_HEART, BLACK_HEART))
            logger.debug('Rate song OK')
        else:
            logger.error(err)

    @current_song_required
    @douban_account_required
    def unrate_current_song(self):
        r, err = self.douban.unrate_song(
            self.current_song.sid, self.current_channel)
        if r:
            self.current_song.like = False
            self.selected_button.set_text(self.selected_button.text.replace(
                BLACK_HEART, WHITE_HEART))
            logger.debug('Unrate song OK')
        else:
            logger.error(err)

    @current_song_required
    @douban_account_required
    def end_current_song(self):
        r, err = self.douban.end_song(
            self.current_song.sid, self.current_channel)
        if r:
            logger.debug('End song OK')
        else:
            logger.error(err)

    @current_song_required
    @douban_account_required
    def trash_current_song(self):
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

    def getChannelListBox(self):
        body = []
        for c in self.channels:
            _channel = ChannelButton(c['name'])
            urwid.connect_signal(
                _channel, 'click', self.on_channel_chosen, c['channel_id'])
            body.append(urwid.AttrMap(_channel, None, focus_map="channel"))
        return ChannelListBox(urwid.SimpleFocusListWalker(body))

    def on_channel_chosen(self, button, choice):
        # Choose the channel which is playing right now, ignore it
        if self.selected_button == button:
            return
        if self.player.is_playing:
            self.player.stop()
        self._choose_channel(choice)
        # Update UI
        if self.selected_button != None and button != self.selected_button:
            self.selected_button.set_text(
                self.selected_button.text[0:11].strip())
        self.selected_button = button
        if self.song_change_alarm:
            self.main_loop.remove_alarm(self.song_change_alarm)
        self._play_track()

    def on_skip(self):
        self.skip_current_song()

    def on_rate_and_unrate(self):
        if self.current_song.like:
            self.unrate_current_song()
        else:
            self.rate_current_song()

    def on_trash(self):
        self.trash_current_song()

    def on_exit(self):
        self.exit()

    def exit(self):
        logger.debug('Exit')
        self.player.stop()
        raise urwid.ExitMainLoop()

    def start(self):
        self.main_loop.run()


def main():
    fm = Doubanfm()
    fm.start()

if __name__ == "__main__":
    main()
