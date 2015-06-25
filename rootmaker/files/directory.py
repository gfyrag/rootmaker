from .file import File 
from .chardevicefile import CharDeviceFile
from .blockdevicefile import BlockDeviceFile
from .simplefile import SimpleFile
import os
import subprocess
import scheme
import packer
import files

class Directory(File):

	def create(self, mode = None):
		if(mode != None): 
			os.makedirs(self.path, mode, True)
		else:
			os.makedirs(self.path, self.mode, True)
		return self
	
	def copytree(self, path):
		shutil.copytree(path, self.path)
		return self

	def listdir(self):
		result = []
		for i in os.listdir(self.path):
			absfilename = self.path + '/' + i
			try:
				result.append(files.discover(absfilename, self))
			except Exception as e:
				print("Error while listing dir : %s (%s)" % (absfilename, e))
		return result

	def export(self, path):
		# Weird behavior with device file
		# print("Export %s to %s" % (self.path, path))
		# shutil.copytree(self.path, path)
		subprocess.check_output(['cp', '-rf', self.path, path])
		return self

	def copy(self, path, enter = False, name = None, mode = None):
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
		file = files.discover(finalPath, self)

		if(mode != None):
			file.chmod(mode)
		else:
			file.chmod(self.mode)
		
		if(enter):
			return file
		else:
			return self

	def in_copy(self, path, name = None, mode = None):
		return self.copy(path, enter = True, name = name, mode = mode)

	def pack(self, format, fileobj):
		packer.factory(format).pack(self.path, fileobj)
		return self

	def unpack(self, format, fileobj):
		packer.factory(format).unpack(self.path, fileobj)
		return self

	def dir(self, path, enter = False, create = True, mode = None):
		dir = Directory(self.path + '/' + path, self)
		if create:
			dir.create()

		if(mode != None):
			dir.chmod(mode)
		else:
			dir.chmod(self.mode)

		if(enter):
			return dir
		else:
			return self

	def in_dir(self, path, create = True):
		return self.dir(path, enter = True, create = create)

	def file(self, name, enter = False, create = True, mode = None):
		file = SimpleFile(self.path + '/' + name, self)
		if create:
			file.create()

		if(mode != None):
			file.chmod(mode)
		else:
			file.chmod(self.mode)

		if(enter):
			return file
		else: 
			return self

	def in_file(self, name, create = True):
		return self.file(name, enter = True, create = create)

	def block_device_file(self, name, major, minor, enter = False, create = True, mode = None):
		file = BlockDeviceFile(self.path + '/' + name, major, minor, self)
		if create:
			file.create()

		if(mode != None):
			file.chmod(mode)
		else:
			file.chmod(self.mode)
		
		if(enter):
			return file
		else:
			return self

	def in_block_device_file(self, name, major, minor, create = True):
		return self.block_device_file(name, major, minor, enter = True, create = create)

	def char_device_file(self, name, major, minor, enter = False, create = True, mode = None):
		file = CharDeviceFile(self.path + '/' + name, major, minor, self)
		if create:
			file.create()

		if(mode != None):
			file.chmod(mode)
		else:
			file.chmod(self.mode)

		if(enter):
			return file
		else:
			return self

	def in_char_device_file(self, name, major, minor, create = True):
		return self.char_device_file(name, major, minor, enter = True, create = create)
