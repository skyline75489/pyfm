# -*- coding: utf-8 -*-
import os
import json
import logging

from hashlib import md5
from getpass import getpass
from collections import deque

try:
    input = raw_input
except NameError:
    pass

HOME_PATH = os.getenv('HOME')
BASIC_PATH = os.path.join(HOME_PATH, '.pyfm')
ACCOUNT_CACHE_PATH = os.path.join(BASIC_PATH, 'account_cache.json')
CHANNELS_CACHE_PATH = os.path.join(BASIC_PATH, 'channels_cache.json')

if not os.path.isdir(BASIC_PATH):
    os.mkdir(BASIC_PATH)

logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s %(message)s',
                    filename=os.path.join(BASIC_PATH, 'fm.log'),
                    level=logging.DEBUG)

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
        self.enable_notify = True

        self.last_fm_username = None
        self.last_fm_password = None
        self.scrobbling = True
        self.douban_account = True

        self.account_cache_path = ACCOUNT_CACHE_PATH
        self.channels_cache_path = CHANNELS_CACHE_PATH

    def do_config(self):
        self.email = input('豆瓣账户 (Email地址): ') or None
        self.password = getpass('豆瓣密码: ') or None
        self.last_fm_username = input('Last.fm 用户名: ') or None
        password = getpass('Last.fm 密码: ') or None
        if password is None:
            self.last_fm_password = None
        else:
            self.last_fm_password = md5(password.encode('utf-8')).hexdigest()
        self.enable_notify = input('是否允许系统通知? (Y/n)').lower() != "n"

    def load_config(self):
        try:
            with open(self.channels_cache_path, 'r') as f:
                self.cached_channels = deque(json.load(f))
            logger.debug("Load channel file.")
        except:
            logger.debug("Channels file not found.")

        try:
            with open(self.account_cache_path, 'r') as f:
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
        except:
            logger.debug("Cache file not found.")

    def save_channel_cache(self, channels):
        try:
            with open(self.channels_cache_path, 'w') as f:
                json.dump(list(channels), f)
        except IOError:
            raise Exception("Unable to write cache file")

    def save_account_cache(self, user_name=None, user_id=None, expire=None, token=None, cookies=None, last_fm_username=None, last_fm_password=None, enable_notify=None):
        if not (user_name or last_fm_username):
            return
        try:
            with open(self.account_cache_path, 'w') as f:
                json.dump({
                    'user_name': user_name,
                    'user_id': user_id,
                    'expire': expire,
                    'token': token,
                    'cookies': cookies,
                    'last_fm_username': last_fm_username,
                    'last_fm_password': last_fm_password,
                    'enable_notify': enable_notify,
                }, f)
        except IOError:
            raise Exception("Unable to write cache file")
