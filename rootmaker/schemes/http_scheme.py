
import requests

def copy(location, path):
	r = requests.get(location)
	with open(path, 'wb') as fd:
		for chunk in r.iter_content(1024):
			fd.write(chunk)
