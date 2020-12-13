import pytest
import crawler as rp

import requests

def test_get_proxy():
	proxy = rp.get_random_proxy()
	assert '.' in proxy
	assert ':' in proxy

def test_process_input():
	crawler_input = {
		'keywords': [
			'openstack',
			'nova',
			'css',
		],
		'proxies': [
			'194.126.37.94:8080',
			'13.78.125.167:8080'
		],
		'type': 'Wikis'
	}
	input_dict = rp.process_input(crawler_input)
	assert input_dict['keywords'] == [
			'openstack',
			'nova',
			'css',
		]
	assert input_dict['proxy'] in [
			'194.126.37.94:8080',
			'13.78.125.167:8080'
		]

	assert input_dict['type'] == 'Wikis'

	with pytest.raises(SystemExit):
		rp.process_input({})

def test_get_repo_details():
	proxy = rp.get_random_proxy()
	details = rp.get_repo_details({'url':'https://github.com/rickfernandes/recursion'},proxy)
	assert details['owner'] == 'rickfernandes'
	assert details['language_stats']['Python'] == 100

def test_language_parser():
	proxy = rp.get_random_proxy()
	proxies = {'http': f'http://{proxy}'}

	r = requests.get('https://github.com/rickfernandes/recursion',proxies=proxies)
	language_stats = rp.languages_parser(r.text)
	assert language_stats == {'Python':100}
