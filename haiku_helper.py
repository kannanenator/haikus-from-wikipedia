from local_settings import *
import tweepy
import re
import nltk
import random_request
import random

class Haikuify(object):

	def __init__(self, wiki_response):
		'''
		Initialize the cmudict and splits up our random response from wikipedia into a list of words
		'''
		text, title, url = wiki_response
		# get rid of title related stuff in the beginning bc it's usually more fun that way :)
		to_drop = len(title.split(' '))
		self.title = ('').join(l for l in title.split(' ') if l.isalpha())
		self.link = url
		self.sylla_dict = cmudict.dict()
		# TODO in the future, maybe improve logic that does the splitting so we have sensible clauses to work with
		self.words = list(filter(lambda x: x != '', re.split('\W', text)))[to_drop:]

	def makeHaiku(self, words):
		'''
		Makes a haiku from our list of words by first turning the words into a list of syllables, 
		then finding indices for combinations of five, seven, and five syllables corresponding to the 
		lines of the haiku. Finally collects those words from our inital list and joins them to 
		return the final Haiku.
		'''

		syllable_list = list(map(self.numSyl, words))
		indices = five_seven_five(syllable_list)
		if indices:
			haiku = (", ").join([(" ").join(words[i[0]:i[1]]) for i in indices])
		else:
			haiku = None

		return haiku

	def numSyl(self, word):
		'''
		Finds the number of syllables in a word, first by trying the nltk cmudict corpus, 
		then resorting to our best guess fallback calculation
		'''

		if self.sylla_dict.get(word.lower()):
			return max([len(list(y for y in x if y[-1].isdigit())) for x in self.sylla_dict[word.lower()]])
		else:
			# fallback if we don't find the word in the dict
			return self.fallback(word.lower())

	def fallback(self, word):
		'''Naive fallback calculation of syllables for words not in the corpus'''

		# Count number of vowel chunks
		syllables = len(list(filter(lambda x: x != '', re.split('[bcdfghjklmnpqrstvwxz0123456789]', word))))

		# Subtract a syllable if there is an e at the end because ending e's usually don't contribute to syllables
		if word[-1] == 'e' and syllables > 1:
			syllables-=1

		# So we dont count the numbers we split
		if syllables == 0:
			syllables = float('inf')

		return syllables

def five_seven_five(syllableList):
	'''Get our haiku word indices!'''

	start = 0
	line_one_indices = find_target_sum(syllableList[start:], 5) 

	start = line_one_indices[1] + 1
	target = find_target_sum(syllableList[start:], 7)

	# Do we still have a part of the syllable list to work with?
	if isinstance(target, str):
		return None	
	line_two_indices = list(map(lambda x: start + x, find_target_sum(syllableList[start:], 7)))

	start = line_two_indices[1] + 1 
	target = find_target_sum(syllableList[start:], 5)

	# Again?
	if isinstance(target, str):
		return None
	line_three_indices = list(map(lambda x: start + x, find_target_sum(syllableList[start:], 5)))

	return line_one_indices, line_two_indices, line_three_indices

def find_target_sum(syllableList, target):
	'''Given a list of syllable counts, find the first contiguous sum that adds up to our target value'''

	start_index = 0
	curr_index = 0
	curr_sum = 0
	while curr_sum != target and start_index < len(syllableList)-1 and curr_index < len(syllableList):
		curr_sum += syllableList[curr_index]
		# increment the start index if we exceed the target
		if curr_sum > target:
			curr_sum = 0
			start_index +=1
			curr_index = start_index
		# if we get the target, return the indices
		elif curr_sum == target:
			return [start_index,(curr_index+1)]
		else:
			curr_index+=1

	return "No suitable combination of syllables"

def connect():
	'''Connect to the twitter API'''
	
	auth = tweepy.OAuthHandler(MY_CONSUMER_KEY, MY_CONSUMER_SECRET)
	auth.set_access_token(MY_ACCESS_TOKEN_KEY, MY_ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

	return api

def post():
	'''Driver to post to twitter'''

	api = connect()
	haiku = None
	title = None
	while haiku == None:
		hf = Haikuify(random_request.get_random_text())
		haiku = hf.makeHaiku(hf.words)
		title = hf.title

	message = haiku + " " + hf.link + " #" + title

	# Only post on average 25% of the time
	i_should_post = random.random() > .75
	if i_should_post:
		print("posting")
		status = api.update_status(message)
	else:
		print("not posting")

if __name__ == "__main__":
	# This is so we have access to the cmudict out on heroku
	nltk.data.path.append('./nltk_data/')
	from nltk.corpus import cmudict
	post()
