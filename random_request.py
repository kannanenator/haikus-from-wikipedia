import requests
from bs4 import BeautifulSoup
import sys

# runs on python 3.5

def request_random():
	'''Request random wikipedia article, return html_doc'''

	r = requests.get('https://en.wikipedia.org/wiki/Special:Random')
	return r.content, r.url

def parse_article(article):
	'''parse html and get relevant (main paragraph) text out the article'''

	soup = BeautifulSoup(article, 'html.parser')
	paragraphs = soup.find_all("p")
	ps = (" ").join([elem.text for elem in paragraphs])
	title = soup.find("h1", id="firstHeading").text
	return ps, title

def get_random_text():
	'''puts the full request together'''
	
	html_doc, url = request_random()
	parsed, title = parse_article(html_doc)
	
	return parsed, title, url

if __name__ == "__main__":
	print(get_random_text())