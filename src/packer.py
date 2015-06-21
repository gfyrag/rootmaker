
import imp
import os

class PackerNotFoundError(Exception):
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "Packet %s not found" % self.name

def factory(name):
	try:
		fp, pathname, description = imp.find_module(name, [os.path.dirname(__file__) + "/packers"])
		return imp.load_module(name, fp, pathname, description)
	except ImportError as e:
		raise PackerNotFoundError(name)