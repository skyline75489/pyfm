豆瓣FM命令行播放器
==================

.. image:: https://badge.fury.io/py/pyfm.png
    :target: http://badge.fury.io/py/pyfm

使用Python编写的豆瓣FM命令行播放器

|Screenshot|

特性
----

-  依赖较少，易于安装和运行
-  支持私人兆赫，红心兆赫
-  支持豆瓣歌曲加心
-  支持Last.fm Scrobble

运行环境
--------

-  Linux/Mac OS X
-  Python 2.7+ , 3.3+

依赖
----

-  `mpg123 <http://www.mpg123.de>`__ (如果安装了 `mpv <http://mpv.io>`__ 或 `mplayer <http://mplayerhq.hu>`__ 亦会自动使用)
-  `requests <https://github.com/kennethreitz/requests>`__
-  `urwid <http://urwid.org>`__

安装
----

::

    (sudo)pip install pyfm

安装依赖
--------

::

    # Linux平台上使用apt-get安装mpg123
    sudo apt-get install mpg123

    # Mac OS X 上使用Homebrew安装
    brew install mpg123

使用
----

::

    $ pyfm

配置
----

::

    $ pyfm config

根据提示输入账户，密码等，豆瓣账户密码不会保存在本地，豆瓣Token，Cookie，Last.fm账户名，Last.fm密码的md5值等保存在$HOME/.pyfm/中。

快捷键
------

::

    [n]  ->  跳过当前歌曲
    [l]  ->  给当前歌曲添加红心或删除红心
    [t]  ->  不再播放当前歌曲
    [q]  ->  退出播放器

致谢
----

本项目主要参考了以下几个项目

-  https://github.com/josephok/doubanfm
-  https://github.com/zonyitoo/doubanfm-qt
-  https://github.com/turingou/douban.fm
-  http://hg.user1.be/ScrobblerPlugin/

感谢以上项目的作者，开源万岁！

Changelog
---------

-  0.2.3 修复若干Bug，加入红心兆赫，支持使用mpv和mplayer作为播放后端(felixonmars)
-  0.2.2 修复登陆失败时登陆状态不能正确显示的Bug
-  0.2.1 修复Last.fm密码为空时报错的Bug
-  0.2   代码大规模重构
-  0.1   第一个正式版本

协议
----

The MIT License

其中\ `scrobbler.py <https://github.com/skyline75489/pyfm/blob/master/pyfm/scrobbler.py>`__\ 遵循GPLv3协议

.. |Screenshot| image:: https://skyline75489.github.io/img/pyfm/screenshot.png
