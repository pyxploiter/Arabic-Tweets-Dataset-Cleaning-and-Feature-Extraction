#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pyarabic.araby as araby
import re
from datetime import date
import cv2
import os
import requests

#8948 tweets
tweets = json.load(open("tweets.json", 'r'))
#5299 users
users = json.load(open("Arabic_users_profiles.json", 'r'))
dataset = dict()

# This regex matches everything but the Arabic letters and shadda.
all_but_arabic_letters = re.compile(u"[^\u0621-\u063A\u0641-\u064A\u0651]", flags=re.UNICODE)

# This regex matches any token that contains no Arabic letters.
# Used to discard Latin and punctuation tokens.
all_but_arabic_letters_in_token = re.compile(u"^[^\u0621-\u063A\u0641-\u064A\u0651]+$", flags=re.UNICODE)

def removeUrl(tweetText):
	return re.sub(r"http\S+", '', tweetText, flags=re.MULTILINE)

def cleanWords(words):
	a_words = []
	for word in words:
		if re.match(all_but_arabic_letters_in_token, word):	# No letters here,
			continue										# get next token.
		clean_word = re.sub(all_but_arabic_letters, "", word)
		a_words.append(clean_word)
	return a_words

#returns count of characters and unique characters
def countChars(tweetText):
	tweetText = araby.strip_tashkeel(tweetText)
	words = araby.tokenize(tweetText) 				#tokenize text into words
	cleaned_words = cleanWords(words)

	add_chars = []
	for word in cleaned_words:
		for char in word:
			add_chars.append(char)
	unique_char = []
	for char in sorted(set(add_chars)):
		times = add_chars.count(char)
		unique_char.append((char,times))
	return len(tweetText), len(unique_char)

#returns count of words and unique words
def countWords(tweetText):
	tweetText = araby.strip_tashkeel(tweetText)
	words = araby.tokenize(tweetText) 				#tokenize text into words
	cleaned_words = cleanWords(words)
	unique_words = []
	for word in sorted(set(cleaned_words)):
		times = cleaned_words.count(word)
		unique_words.append((word, times))
	
	return len(cleaned_words), len(unique_words)

#count any symbol in text
def countMe(tweetText, what):
	parts = tweetText.split(what)
	return 0 if len(parts) == 0 else len(parts)-1

#count special symbols in text
def countSpecialSymbol(tweetText):
	count = 0
	tweetText = araby.strip_tashkeel(tweetText)
	text = removeUrl(tweetText)
	
	special_symbols = u"!@#$%^&*()_+-/;:></?`~=“”"
	for schar in special_symbols:
		count += countMe(text, schar)
	return count

def hasUrlShortner(tweetText):
	return True if (countMe(tweetText, "http://t.co/") > 0) else False 

#calculates author's registration age
def calculateAuthorAge(publishDate, registrationDate):
	charM_intM = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5,"Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
	
	p_day = int(publishDate[8:10])
	p_month = charM_intM[publishDate[4:7]]
	p_year = int(publishDate[26:30])
	
	r_day = int(registrationDate[8:10])
	r_month = charM_intM[registrationDate[4:7]]
	r_year = int(registrationDate[26:30])

	registrationAge = date(p_year, p_month, p_day) - date(r_year, r_month, r_day)
	
	return registrationAge.days

#function for computing author's details
def computeAuthorDetail(author, tweetTime):
	tweetText = ""
	totalTweetLength = 0
	totalHashtags = 0
	totalUrls = 0
	totalMentions = 0
	totalFollowers = 0
	totalFriends = 0
	totalRetweets = 0
	num_of_tweets = 0
	tweets_till_now = 0
	timeSpace = 0

	charM_intM = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5,"Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
	
	p_day = int(tweetTime[8:10])
	p_month = charM_intM[tweetTime[4:7]]
	p_year = int(tweetTime[26:30])

	for tweet in tweets:
		if(tweet["userid"] == author):
			num_of_tweets += 1
			tweetText = araby.strip_tashkeel(tweet["text"])
			totalTweetLength += len(tweetText)
			totalHashtags += countMe(tweet["text"],"#")
			totalUrls += countMe(tweet["text"],"http://t.co/")
			totalMentions += countMe(tweet["text"],"@")
			totalFollowers += tweet["followerscount"]
			totalFriends += tweet["friendcount"]
			if (tweet["retweeted"] == True):
				totalRetweets+=1

			tweetDate = tweet["creationdate"]
			t_day = int(tweetDate[8:10])
			t_month = charM_intM[tweetDate[4:7]]
			t_year = int(tweetDate[26:30])

			if (date(p_year, p_month, p_day) > date(t_year, t_month, t_day)):
				tweets_till_now += 1
				timeSpace += (date(p_year, p_month, p_day) - date(t_year, t_month, t_day)).days
							
	totalFriends = 1 if totalFriends == 0 else totalFriends
	totalFollowers = 1 if totalFollowers == 0 else totalFollowers
	totalMentions = 1 if totalMentions == 0 else totalMentions
	tweets_till_now = 1 if tweets_till_now == 0 else tweets_till_now 

	fo_fe = totalFollowers/(totalFriends*1.0)
	fe_fo = totalFriends/(totalFollowers*1.0)
	avgTweetLength = totalTweetLength/num_of_tweets
	url_mention_ratio = totalUrls/(totalMentions*1.0)
	avgHashtags = totalHashtags/num_of_tweets
	retweetFraction = totalRetweets/(num_of_tweets-totalRetweets)
	tweetTimeSpacing = timeSpace/(tweets_till_now*1.0)

	return fo_fe, fe_fo, avgTweetLength, url_mention_ratio, avgHashtags, retweetFraction, tweetTimeSpacing

#It downloads image from url then detects if there is face in it
#returns True if image holds face otherwise returns False
def detectFace(imgUrl):
	imgExtention = imgUrl.split(".")
	imgExtention = str(imgExtention[len(imgExtention)-1])
	imgUrlWithOutExtention = (imgUrl.split(imgExtention))[0]
	fullImgUrl = (imgUrlWithOutExtention.replace("_normal","_400x400"))+imgExtention
	
	#if image url is valid, download the image and store it as "AuthorImage.jpg"
	try:
		img_data = requests.get(fullImgUrl).content
		with open('AuthorImage.jpg', 'wb') as handler:
			handler.write(img_data)
	except:
		pass

	#read author image
	img = cv2.imread("AuthorImage.jpg")
	#select cascade classifier
	cascade = cv2.CascadeClassifier("haarcascade_face_alt.xml")
	#apply classifier to image and get contour of face (if there is any)
	rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
	#if there is no rects (contour), it means there is no face in image
	if len(rects) == 0:
		return False
	#if found some rects, return True as there is a face in image
	else:
		return True

print "Total tweets found in tweets dataset: "+str(len(tweets))
print "Total users found in users dataset: "+str(len(users))
x = 0
#looping through all tweets
for tweet in tweets:
	for user in users:
		if (int(user["id"]) == int(tweet["userid"])):
			x+=1
			key = int(tweet["tweetid"])
			value = []
			count_words, count_unique_words = countWords(tweet["text"])
			count_chars, count_unique_chars = countChars(tweet["text"])
			fo_fe, fe_fo, avgTweetLength, url_mention_ratio, avgHashtags, retweetFraction, tweetTimeSpacing = computeAuthorDetail(tweet["userid"], tweet["creationdate"])

			value.append(countMe(tweet["text"], "@"))				#count of mentions
			value.append(count_chars)								#count of chars
			value.append(count_words)								#count of words
			value.append(countMe(tweet["text"], "#"))				#count of hashtags 
			value.append(count_unique_words)						#count of unique words 
			value.append(count_unique_chars)						#count of unique chars 
			value.append(countMe(tweet["text"], "?"))				#count of question marks
			value.append(countMe(tweet["text"], "!"))				#count of exclamation marks
			value.append(countMe(tweet["text"], "..."))				#count of ellipses
			value.append(countSpecialSymbol(tweet["text"]))			#count of special symbols
			value.append(fo_fe)										#follower/friend ratio of author
			value.append(fe_fo)										#friend/follower ratio of author
			value.append(hasUrlShortner(tweet["text"]))				#used url shortner
			value.append(tweet["retweeted"])						#tweet is a retweet (True/False)
			value.append(str(tweet["creationdate"][0:3]))			#day of week of publishing the tweet
			value.append(calculateAuthorAge(tweet["creationdate"],tweet["creationdate1"])) 	#Registration age of author in days
			value.append(detectFace(tweet["imageurlhttps"]))		#detecting if author's image holds a face
			value.append(tweetTimeSpacing)
			value.append(avgTweetLength)							#Average tweet time spacing of author in days
			value.append(url_mention_ratio)							#Url/mention ratio in tweets of author
			value.append(avgHashtags)								#Average of hashtags of author
			value.append(retweetFraction)							#retweet fraction of the author
			value.append(user["listed_count"])
			row = {key: value}										#creating row
			dataset.update(row)										#updating dataset
			print str(x)+") Tweet #"+str(key)+" processed." 
			print row
			break

#storing the dataset in output.json file
json.dump(dataset, open("output.json","w"))
