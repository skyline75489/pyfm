# -*- coding: utf-8 -*-
import json
import logging

from getpass import getpass
from collections import deque

logger = logging.getLogger()


class Config(object):
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
        
    def do_config(self):
        self.email = input('豆瓣账户 (Email地址): ') or None
        self.password = getpass('豆瓣密码: ') or None
        self.last_fm_username = input('Last.fm 用户名: ') or None
        password = getpass('Last.fm 密码: ') or None
        self.last_fm_password = md5(password.encode('utf-8')).hexdigest()

    def load_config(self):
        try:
            f = open('channels.json', 'r')
            self.channels = deque(json.load(f))
            logger.debug("Load channel file.")
        except Exception as e:
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

        except Exception as e:
            logger.debug("Cache file not found.")

    def save_cache(self, fm):
        f = None
        try:
            f = open('cache.json', 'w')
            f2 = open('channels.json', 'w')
            json.dump({
                'user_name': fm.douban.user_name,
                'user_id': fm.douban.user_id,
                'expire': fm.douban.expire,
                'token': fm.douban.token,
                'cookies': fm.douban.cookies,
                'last_fm_username': self.last_fm_username,
                'last_fm_password': self.last_fm_password
            }, f)
            json.dump(list(fm.channels), f2)
        except IOError:
            raise Exception("Unable to write cache file")