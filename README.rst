豆瓣FM命令行播放器
==================

**2015-11-16 更新：豆瓣客户端接口被封锁，本项目处于不可用状态。**

**可用的类似项目（目前使用网易云音乐）： https://github.com/taizilongxu/douban.fm**

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

请首先安装支持的后端播放器中的某一个，然后使用pip安装本软件：

::

    (sudo)pip install pyfm
    

如果选择直接git clone整个仓库的方法安装，请先安装相关依赖，然后把pyfm目录下的fm.py移动到上层目录，最后执行 `python fm.py` 


使用
----

在终端中输入

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


出现问题？
-----------

请尝试清空$HOME/.pyfm/目录下的所有内容，重新安装等，如还不能解决，欢迎向我提issue。

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

-  0.2.4 修复若干问题，支持关闭通知
-  0.2.3 修复若干Bug，加入红心兆赫，支持使用mpv和mplayer作为播放后端(`felixonmars <https://github.com/felixonmars>`__)
-  0.2.2 修复登陆失败时登陆状态不能正确显示的Bug
-  0.2.1 修复Last.fm密码为空时报错的Bug
-  0.2   代码大规模重构
-  0.1   第一个正式版本

协议
----

The MIT License

其中\ `scrobbler.py <https://github.com/skyline75489/pyfm/blob/master/pyfm/scrobbler.py>`__\ 遵循GPLv3协议

.. |Screenshot| image:: https://skyline75489.github.io/img/pyfm/screenshot.png
