豆瓣FM命令行播放器
==================

使用Python编写的豆瓣FM命令行播放器

![Screenshot](https://skyline75489.github.io/img/pyfm/screenshot.png)

## 特性

* 依赖较少，易于安装和运行
* 支持Last.fm Scrobble
* 支持豆瓣歌曲加心

## 运行环境

* Linux/Mac OS X
* Python 2.7+ , 3.3+

## 依赖

* [mpg123](http://www.mpg123.de)
* [requests](https://github.com/kennethreitz/requests)
* [urwid](http://urwid.org)

## 安装
   
    git clone https://github.com/skyline75489/pyfm.git
    
## 安装依赖

    # Linux平台上使用apt-get安装mpg123
    sudo apt-get install mpg123
    
    # Mac OS X 上使用Homebrew安装
    brew install mpg123
    
    # 如果没有安装pip，请先安装pip
    # 然后再使用pip安装下面的依赖
    (sudo) pip install requests
    (sudo) pip install urwid

## 使用

    python pyfm.py

## 配置

    python pyfm.py config
    
根据提示输入账户，密码等，豆瓣账户密码不会保存在本地，豆瓣Token，Cookie，Last.fm账户名，Last.fm密码的md5值等保存在cache.json中。

## 快捷键
    [n]  ->  跳过当前歌曲
    [l]  ->  给当前歌曲添加红心或删除红心
    [t]  ->  不再播放当前歌曲
    [q]  ->  退出播放器

## 致谢

本项目主要参考了以下几个项目

* https://github.com/josephok/doubanfm
* https://github.com/zonyitoo/doubanfm-qt
* https://github.com/turingou/douban.fm
*  http://hg.user1.be/ScrobblerPlugin/

感谢以上项目的作者，开源万岁！

## Changelog

* 0.1 第一个正式版本

## 协议

The MIT License

其中[scrobbler.py](https://github.com/skyline75489/pyfm/blob/master/scrobbler.py)遵循GPLv3协议
