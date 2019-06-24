# Arabic Tweets Dataset cleaning and feature extraction
## Dataset Cleaning
##### -> Removing Non-arabic Words from tweets
##### -> Removing URLs from tweets
## Features
##### -> Count of characters, unique characters, words, unique words
##### -> Count of mentions, hashtags
##### -> Count of question marks, exclamation marks, ellipses
##### -> Count of special symbols 
##### -> Follower/Friend ratio
##### -> Friend/Follower ratio
##### -> used url shortener?
##### -> isRetweet?
##### -> day of week of publishing the tweet
##### -> Registration age of author in days
##### -> Detecting if author profile image has a face
##### -> Average tweet time spacing of author in days
##### -> Url/mention ratio in tweets of author
##### -> Average of hashtags of author
##### -> Retweet fraction of the author

## You need to install following python libraries to run this script:
1) pyarabic
2) opencv-python

If you have already installed 'pip' then these libraries can be easily installed, just run following commands:

<b>for windows:</b>
```shell
$ pip install pyarabic
$ pip install opencv-python
```
<b>for linux (ubuntu):</b>
```shell
$ sudo pip install pyarabic
$ sudo pip install opencv-python
```
<b>After installing the libraries, run this script:</b>
```shell
$ python script.py
```
