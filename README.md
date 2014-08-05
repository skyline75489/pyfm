豆瓣FM命令行播放器
==================

使用Python编写的豆瓣FM命令行播放器

![Screenshot](https://skyline75489.github.io/img/pyfm/screenshot.png)

尚在开发中。

## 运行环境

* Linux/Mac OS X
* Python 3.4

只在Mac OS X和Linux Mint 14(Ubuntu 12.10)环境上进行了测试。大部分Unix/Linux上应该都能够正常工作。

## 依赖

* [requests](https://github.com/kennethreitz/requests)
* [mpg123](http://www.mpg123.de)
* [urwid](http://urwid.org)

## 安装依赖

    pip3 install requests
    pip3 install urwid
    # on Linux with apt-get
    sudo apt-get install mpg123
    # on Mac OS X with Homebrew
    brew install mpg123

## 配置文件

config.json

    {
        "email": 豆瓣用户名,
        "password": 豆瓣密码,
        "last_fm_username": Last.fm用户名,
        "last_fm_password": Last.fm密码
    }

## 使用

    python3 pyfm.py

## 快捷键
    [n]  ->  跳过当前歌曲
    [l]  ->  给当前歌曲添加红心或删除红心
    [t]  ->  不再播放当前歌曲
    [q]  ->  退出播放器

## 感谢

本项目主要参考了以下几个项目

* https://github.com/josephok/doubanfm
* https://github.com/zonyitoo/doubanfm-qt
* https://github.com/turingou/douban.fm
*  http://hg.user1.be/ScrobblerPlugin/

感谢以上项目的作者，开源万岁！

## 协议

The MIT License
