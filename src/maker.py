#!/usr/bin/env python3

import os
import tempfile
import stat
import chroot
import packer
import shutil
import abc
import subprocess
import scheme

class File:
	def __init__(self, path):
		self.path = path

	def __str__(self):
		return self.path

	def parent(self):
		return Directory(os.path.dirname(self.path))

	def chmod(self, mode, recursive = False):
		command = 'chmod '
		if recursive:
			command += '-Rf '
		command += oct(mode)[2:] + ' ' + self.path
		subprocess.check_output(command.split())
		# os.chmod(self.path, mode)
		return self

	def size(self):
		return int(subprocess.check_output(['du', '-shb', self.path]).split()[0].decode('utf-8'))

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
			try:
				return SymlinkFile(path, os.path.realpath(path))
			except:
				return SymlinkFile(path, None)
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


class BlockDeviceFile(DeviceFile):

	def __init__(self, path, major, minor):
		DeviceFile.__init__(self, path, stat.S_IFBLK, major, minor)

class CharDeviceFile(DeviceFile):

	def __init__(self, path, major, minor):
		DeviceFile.__init__(self, path, stat.S_IFCHR, major, minor)

class FIFOFile(File): pass

class SocketFile(File): pass

class SimpleFile(File):

	def create(self, mode = 0o777):
		with open(self.path, 'w'):
			pass
		return self.chmod(mode)

	def write(self, data):
		file = os.open(self.path, os.O_CREAT|os.O_WRONLY)
		os.write(file, bytes(data, 'UTF-8'))
		os.close(file)
		return self

class SymlinkFile(File):

	def __init__(self, path, target):
		self.target = target
		File.__init__(self, path)

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
				print("Error while listing dir : %s (%s)" % (absfilename, e))

		return result

	def export(self, path):
		# Weird behavior with device file
		#print("Export %s to %s" % (self.path, path))
		#shutil.copytree(self.path, path)
		subprocess.check_output(['cp', '-rf', self.path, path])
		return self

	def copy(self, path, name = None):
		if name == None:
			filename = os.path.basename(path)
		else:
			filename = name

		parts = path.split('://')
		if(len(parts) > 1):
			fileScheme = parts[0]
		else:
			fileScheme = 'file'

		finalPath = self.path + '/' + filename

		scheme.factory(fileScheme).copy(path, finalPath)
		
		return File.discover(finalPath)

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
			def callback():
				return subprocess.call(command, shell=False)
			return env.call(callback)
	
