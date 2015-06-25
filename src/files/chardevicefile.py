from .devicefile import DeviceFile
import stat 

class CharDeviceFile(DeviceFile):
	def __init__(self, path, major, minor, previous):
		DeviceFile.__init__(self, path, stat.S_IFCHR, major, minor, previous)
