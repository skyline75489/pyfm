豆瓣FM命令行播放器
==================

使用mpg123进行解码，豆瓣FM API来自 https://github.com/josephok/doubanfm 。

尚在开发中。



## 运行环境

* Linux/Mac OS X
* Python 3

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

    python pyfm.py

目前默认播放的是欧美频道

使用mpg123的内置控制，按f或q跳过当前歌曲。
