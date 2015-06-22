
import imp
import os

class SchemeNotFoundError(Exception):
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "Scheme %s not found" % self.name

def factory(name):
	name += '_scheme'
	try:
		fp, pathname, description = imp.find_module(name, [os.path.dirname(__file__) + "/schemes"])
		return imp.load_module(name, fp, pathname, description)
	except ImportError as e:
		raise SchemeNotFoundError(name)