from .file import File
from .devicefile import DeviceFile
from .chardevicefile import CharDeviceFile
from .blockdevicefile import BlockDeviceFile 
from .directory import Directory
from .fifofile import FIFOFile 
from .simplefile import SimpleFile 
from .socketfile import SocketFile 
from .symlinkfile import SymlinkFile 
import os
import stat

global discover
def discover(path, previous):
	statInfo = os.lstat(path)
	if(stat.S_ISDIR(statInfo.st_mode)):
		return Directory(path, previous)
	elif(stat.S_ISREG(statInfo.st_mode)):
		return SimpleFile(path, previous)
	elif(stat.S_ISLNK(statInfo.st_mode)):
		try:
			return SymlinkFile(path, os.path.realpath(path), previous)
		except:
			return SymlinkFile(path, None, previous)
	elif(stat.S_ISBLK(statInfo.st_mode)):
		# TODO : Get major/minor
		return BlockDeviceFile(path, 0, 0, previous)
	elif(stat.S_ISCHR(statInfo.st_mode)):
		# TODO : Get major/minor
		return CharDeviceFile(path, 0, 0, previous)
	elif(stat.S_ISFIFO(statInfo.st_mode)):
		return FIFOFile(path, previous)
	elif(stat.S_ISSOCK(statInfo.st_mode)):
		return SocketFile(path, previous)
	else:
		raise RuntimeError('File %s : Type unknown' % path)