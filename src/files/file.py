import abc
import subprocess

class File:
	def __init__(self, path, previous):
		self.path = path
		self.previous = previous
		self._mode = None

	def __str__(self):
		return self.path

	def up(self):
		return self.previous

	@property
	def mode(self):
		if(self._mode != None):
			return self._mode
		elif(self.previous != None):
			return self.previous.mode
		else:
			return 0o600	

	def current_mode(self, value):
		self._mode = value

		return self

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
	def create(self, mode = None): pass