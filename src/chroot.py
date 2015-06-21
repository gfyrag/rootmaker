
import subprocess
import os
import tempfile

class ChrootEnvironment:

	def __init__(self, rootfs):
		self.lowerdir = tempfile.TemporaryDirectory()
		self.workdir = tempfile.TemporaryDirectory()
		self.mountpoint = tempfile.TemporaryDirectory()
		self.rootfs = rootfs

	def __enter__(self):

		# Create necessary structure for the chroot
		os.mkdir(self.lowerdir.name + '/dev')
		os.mkdir(self.lowerdir.name + '/proc')
		os.mkdir(self.lowerdir.name + '/sys')
		os.mkdir(self.lowerdir.name + '/etc')

		# Create a fake resolv.conf to allow bind mount
		with open(self.lowerdir.name + '/etc/resolv.conf', 'a'):
			pass

		# Mount layers
		subprocess.check_call(['mount', 'none', '-t', 'overlay', '-o', \
			'lowerdir=' + self.lowerdir.name + ',upperdir=' + self.rootfs.name + ',workdir=' + self.workdir.name, self.mountpoint.name])

		# Mount necessary 
		subprocess.check_call(['mount', '--bind', '/dev', self.mountpoint.name + '/dev'])
		subprocess.check_call(['mount', '--bind', '/proc', self.mountpoint.name + '/proc'])
		subprocess.check_call(['mount', '--bind', '/sys', self.mountpoint.name + '/sys'])
		subprocess.check_call(['mount', '--bind', '/etc/resolv.conf', self.mountpoint.name + '/etc/resolv.conf'])

		return self

	def __exit__(self, type, value, trackback):
		subprocess.check_call(['umount', self.mountpoint.name + '/dev'])
		subprocess.check_call(['umount', self.mountpoint.name + '/proc'])
		subprocess.check_call(['umount', self.mountpoint.name + '/sys'])
		subprocess.check_call(['umount', self.mountpoint.name + '/etc/resolv.conf'])
		subprocess.check_call(['umount', self.mountpoint.name])

	def call(self, command):
		subprocesspid = os.fork()
		if subprocesspid == 0: # We're in the child
			os.chroot(self.mountpoint.name)
			newRoot = os.open('/', os.O_RDONLY)
			os.fchdir(newRoot)

			# Use os._exit() to not raising SystemExit and not called __exit__ of the ChrootEnvironment 
			# for the subprocess (whill will result in an exception since paths it's the responsibility of the main process to handle this)
			status = subprocess.call(command, shell=True)
			os.close(newRoot)
			os._exit(status)
		else:
			return os.waitpid(subprocesspid, 0)