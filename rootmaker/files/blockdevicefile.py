from .devicefile import DeviceFile
import stat 

class BlockDeviceFile(DeviceFile):
	def __init__(self, path, major, minor, previous):
		DeviceFile.__init__(self, path, stat.S_IFBLK, major, minor, previous)
