豆瓣FM命令行播放器
==================

主要参考 https://github.com/josephok/doubanfm 和 https://github.com/zonyitoo/doubanfm-qt。 在josephok项目的基础上对代码进行了完全的重构。

豆瓣FM API参考 https://github.com/zonyitoo/doubanfm-qt/wiki/豆瓣FM-API

使用mpg123进行解码，

尚在开发中。



## 运行环境

* Linux/Mac OS X
* Python 3

只在Mac OS X上的Python 3.4环境下进行了测试。大部分Unix/Linux上应该都能够正常工作。

## 依赖

* [requests](https://github.com/kennethreitz/requests)
* [mpg123](http://www.mpg123.de)

## 安装依赖

    pip3 install requests
    # on Linux with apt-get
    sudo apt-get install mpg123
    # on Mac OS X with Homebrew
    brew install mpg123

## 使用

    python3 pyfm.py

目前默认播放的是欧美频道，使用mpg123的内置控制，按f或q跳过当前歌曲。
