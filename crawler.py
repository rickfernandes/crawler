"""
Crawler to get results from specific query from github.com.

__External modules__: `requests`, `random`, `random`, `bs4`, `json`

`Compatible with Python3.8 or higher`
"""
import requests
from random import randint
from bs4 import BeautifulSoup
import json


def get_random_proxy(*args):
	"""Function to wait process thread responsible for calculation the solutions.

	Args:
		proxies (array): _Optional_ array of `str` with proxies

	Returns:
		proxy (str): a random proxy
	"""
	if not args:
		http_proxies = [
			'200.68.49.184:8080',
			'119.252.160.165:3128',
			'94.180.249.187:38051',
			'62.210.69.176:5566' ]
	else:
		http_proxies = args[0]

	n = randint(0,len(http_proxies)-1)

	return http_proxies[n]

def process_input(crawler_input):
	"""Function process the input, making sure it is valid.

	Args:
		crawler_input (dict): `dict` with `keywords`, `proxies` and `type`

	Returns:
		input_dict (dict): a sanatised `dict` with the inputs for the crawler
	"""
	try: 
		keywords = crawler_input['keywords']
	except KeyError: 
		print('No keywords found')
		quit()

	try: 
		proxy = get_random_proxy(crawler_input['proxies'])
	except KeyError: 
		print('No proxies found, using existing ones') 
		proxy = get_random_proxy()

	try:
		query_type = crawler_input['type']
	except KeyError:
		print('No type found')
		quit()

	if query_type not in ['Repositories','Issues', 'Wikis']:
		print('Invalid type')
		quit()


	input_dict = {
		'keywords': keywords,
		'proxy': proxy,
		'type': query_type
	}

	return input_dict

def parse_keywords(keywords):
	"""Function to convert the keywords `array` in to a `str` that will be used for the crawler query

	Args:
		keywords (array): `array` with `keywords`

	Returns:
		formated_keyword (str): `str` with the concatenated keywords using + between them
	"""
	q = ''
	for i in range(len(keywords)): 
		q += f'{keywords[i]}+'
	return q[0:-1]


def get_results_page(input_dict):
	"""Function to retrieve the first 10 results for the specified input

	Args:
		input_dict (dict): `dict` with crawler input

	Returns:
		page (str): `str` with the html content of the page
	"""
	q = parse_keywords(input_dict['keywords'])
	proxy_dict = {'http': f'http://{input_dict["proxy"]}'}
	search_type = input_dict['type']

	r = requests.get(f'https://github.com/search?q={q}&type={search_type}', proxies=proxy_dict)

	return r.text

def results_parser(page):
	"""Function to parse the result page

	Args:
		page (str): `str` with html content

	Returns:
		results_dict (dict): `dict` with the results from the crawler
	"""
	results_dict = {}

	soup_page = BeautifulSoup(page, 'html.parser')
	results = soup_page.findAll('div', {'class':'f4 text-normal'})

	for result in results:
		temp = result.find('a').get('data-hydro-click')
		json_input = json.loads(temp)
		payload = json_input['payload']
		results_dict[payload['result_position']] = payload
	
	return results_dict

def languages_parser(page):
	"""Function to parse the languages in a repository page

	Args:
		page (str): `str` with html content

	Returns:
		language_stats (dict): `dict` with the language status of the repository
	"""
	language_stats = {}

	soup_page = BeautifulSoup(page, 'html.parser')
	languages = soup_page.findAll('li', {'class': 'd-inline'})
	for language in languages:
		temp = language.find('span',{'class': 'text-gray-dark text-bold mr-1'})
		lang = temp.get_text()
		value = temp.findNext('span').get_text()
		language_stats[lang] = float(value.strip('%'))

	return language_stats

def get_urls(results_dict):
	"""Function to get the url of each result in the results `dict`

	Args:
		results_dict (dict): `dict` with all the results

	Returns:
		url (array): `array` with the urls of returned by the crawler
	"""
	urls = []
	for result in results_dict:
		url = results_dict[result]['result']['url']
		urls.append({"url":url})
	return urls

def get_repo_details(url,proxy):
	"""Function to get the details of a specific repository

	Args:
		url (dict): `dict` with all the results format {'url': url_str}\n
		proxy(str): `str` with the proxy to be used


	Returns:
		repo_details (dict): `dict` with the repository details
	"""
	temp = url['url'].replace('https://github.com/','')
	owner = temp[0:temp.find("/")]
	
	proxies = {'http': f'http://{proxy}'}
	
	r = requests.get(url['url'],proxies=proxies)
	
	language_stats = languages_parser(r.text)
	return {'owner': owner, 'language_stats': language_stats }

def crawler(crawler_input):
	"""Function to crawl the webpage using the inputs given by the user

	Args:
		crawler_input (dict): `dict` with the crawler input

	Returns:
		details (json): an indented json object with all the crawler information
	"""
	c_input = process_input(crawler_input)
	text = get_results_page(c_input)
	results_dict = results_parser(text)
	urls = get_urls(results_dict)

	if c_input['type'] == 'Repositories':
		for url in urls:
			url['extra'] = get_repo_details(url,c_input['proxy'])
			

	return json.dumps(urls,indent=1)

def memory_usage(method,args):
	"""Function to check the memory usage

	Args:
		method (function): `function` to be evaluated\n
		args (args): `args` to be used on the evalutated method

	Returns:
		__Nonen__
	"""
	import tracemalloc
	tracemalloc.start()

	method(args)
	
	current, peak = tracemalloc.get_traced_memory()
	print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
	tracemalloc.stop()

if __name__ == '__main__':
	crawler_input = {
		'keywords': [
			'recursion',
			# 'rickfernandes',
			# 'css',
			# 'rick',
			# 'otrisus'
		],
		'proxies': [
			'194.126.37.94:8080',
			'13.78.125.167:8080'
		],
		'type': 'Repositories'
	}
	
	print(crawler(crawler_input))

	# memory_usage(crawler,crawler_input)


	
