from .file import File
import os

class DeviceFile(File):

	def __init__(self, path, type, major, minor, previous):
		self.type = type
		self.major = major
		self.minor = minor
		File.__init__(self, path, previous)

	def create(self, mode = None):
		device = os.makedev(self.major, self.minor)
		if(mode != None):
			os.mknod(self.path, self.type|mode, device)
		else:
			os.mknod(self.path, self.type|self.mode, device)
		return self