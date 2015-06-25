from .file import File
import os

class SimpleFile(File):

	def create(self, mode = None):
		with open(self.path, 'w'):
			pass
		if(mode != None):
			return self.chmod(mode)
		else:
			return self.chmod(self.mode)

	def write(self, data):
		file = os.open(self.path, os.O_CREAT|os.O_WRONLY)
		os.write(file, bytes(data, 'UTF-8'))
		os.close(file)
		return self