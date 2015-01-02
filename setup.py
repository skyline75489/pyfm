from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="pyfm",
    version="0.2.4",
    license="MIT",
    description="A Tiny and Smart Terminal Player of douban.fm ",
    author='skyline75489',
    author_email='skyline75489@outlook.com',
    url='https://github.com/skyline75489/pyfm',
    packages=['pyfm'],
    install_requires=[
        'requests>=2.0.0',
        'urwid>=1.2.1'
    ],
    entry_points={
        'console_scripts': ['pyfm = pyfm.fm:main'],
    },
    classifiers=[
        'Environment :: Console',
        'Environment :: Console :: Curses', 
        'Intended Audience :: End Users/Desktop',     
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix', 
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Sound/Audio :: Players'
    ],
    long_description=long_description,
)
