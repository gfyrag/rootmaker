#!/usr/bin/env python3

import os
import tempfile
import stat
import chroot
import packer
import shutil
import abc

class File:
	def __init__(self, path):
		self.path = path

	def __str__(self):
		return self.path

	def chmod(self, mode):
		os.chmod(self.path, mode)
		return self

	def size(self):
		return os.stat(self.path).st_size

	@abc.abstractmethod
	def create(self, mode = 0o0777): pass

	@staticmethod
	def discover(path):
		statInfo = os.lstat(path)
		if(stat.S_ISDIR(statInfo.st_mode)):
			return Directory(path)
		elif(stat.S_ISREG(statInfo.st_mode)):
			return SimpleFile(path)
		elif(stat.S_ISLNK(statInfo.st_mode)):
			return SymlinkFile(path, os.path.realpath(absfilename))
		elif(stat.S_ISBLK(statInfo.st_mode)):
			# TODO : Get major/minor
			return BlockDeviceFile(path, 0, 0)
		elif(stat.S_ISCHR(statInfo.st_mode)):
			# TODO : Get major/minor
			return CharDeviceFile(path, 0, 0)
		elif(stat.S_ISFIFO(statInfo.st_mode)):
			return FIFOFile(path)
		elif(stat.S_ISSOCK(statInfo.st_mode)):
			return SocketFile(path)
		else:
			raise RuntimeError('File %s : Type unknown' % path)


class DeviceFile(File):

	def __init__(self, path, type, major, minor):
		self.type = stat.S_IFBLK
		self.major = major
		self.minor = minor
		File.__init__(self, path)

	def create(self, mode = 0o0777):
		device = os.makedev(self.major, self.minor)
		os.mknod(self.path, self.type|mode, device)
		return self

class BlockDeviceFile(File):

	def __init__(self, path, major, minor):
		DeviceFile.__init__(self, path, stat.S_IFBLK, major, minor)

class CharDeviceFile(File):

	def __init__(self, path, major, minor):
		DeviceFile.__init__(self, path, stat.S_IFCHR, major, minor)

class FIFOFile(File): pass

class SocketFile(File): pass

class SimpleFile(File):

	def create(self, mode = 0o0777):
		with open(self.path, os.O_CREAT, mode = mode):
			pass
		return self

	def write(self, data):
		file = os.open(self.path, os.O_CREAT|os.O_WRONLY)
		os.write(file, bytes(data, 'UTF-8'))
		os.close(file)
		return self

class SymlinkFile(File):

	def __init__(self, path, target):
		self.target = target
		File.__init__(self, path)

	def size(self):
		return 0

class Directory(File):

	def create(self, mode = 0o0777): 
		os.makedirs(self.path, mode, True)
		return self
	
	def copytree(self, path): 
		shutil.copytree(path, self.path)
		return self

	def listdir(self):
		result = []
		for i in os.listdir(self.path):
			absfilename = self.path + '/' + i
			try:
				result.append(File.discover(absfilename))
			except Exception as e:
				print("Error while listing dir : %s" % absfilename)

		return result

	def size(self):
		total = 0
		files = self.listdir()
		for f in files:
			size = f.size()
			print("Size of %s : %s (%s)" % (f.path, size, type(f)))
			total += size

		return total

	def export(self, path):
		shutil.copytree(self.path, path)
		return self

	def copy(self, path):
		filename = os.path.basename(path)
		shutil.copy2(path, self.path + '/' + filename)
		return self

	def pack(self, format, fileobj):
		packer.factory(format).pack(self.path, fileobj)
		return self

	def unpack(self, format, fileobj):
		packer.factory(format).unpack(self.path, fileobj)
		return self

	def dir(self, path):
		return Directory(self.path + '/' + path)

	def file(self, name):
		return SimpleFile(self.path + '/' + name)

	def block_device_file(self, name, major, minor):
		return BlockDeviceFile(self.path + '/' + name, major, minor)

	def char_device_file(self, name, major, minor):
		return CharDeviceFile(self.path + '/' + name, major, minor)

class RootMaker:

	def __init__(self):
		self.rootfs = tempfile.TemporaryDirectory()

	# Manipulate files
	def root(self):
		return Directory(self.rootfs.name)
		
	# Execute commands
	def chroot(self, command):
		with chroot.ChrootEnvironment(self.rootfs) as env:
			return env.call(command)
	
