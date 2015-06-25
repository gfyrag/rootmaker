#!/usr/bin/env python3

import tempfile
import chroot
import subprocess

import scheme
import abc
import shutil
import packer
import os
import stat

from files import Directory

class RootMaker:

	def __init__(self):
		self.rootfs = tempfile.TemporaryDirectory()

	# Manipulate files
	def root(self):
		return Directory(self.rootfs.name, None)
		
	# Execute commands
	def chroot(self, command):
		with chroot.ChrootEnvironment(self.rootfs) as env:
			def callback():
				return subprocess.call(command, shell=False)
			return env.call(callback)
	
