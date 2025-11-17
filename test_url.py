import requests
import re

regex_content = re.compile(r'<img[^>]+src=["\'](.*?)["\'][^>]*/?>', re.IGNORECASE | re.MULTILINE);

url = "https://www.doctolib.fr/osteopathe/cannes/jean-marc-gabriel"

try:
	response = requests.get(url, headers={
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
	})
except requests.exceptions.RequestException as e:
	print('An error occured during the request: ', e)

all_image = regex_content.findall(response.text)

for(img_url) in all_image:
	print('Found image URL: ', img_url)
	if(not img_url.startswith('https')):
		img_url = 'https:' + img_url
	requests.get(img_url, headers={
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
	})
	print('Downloaded image from URL: ', img_url)

open('i')
