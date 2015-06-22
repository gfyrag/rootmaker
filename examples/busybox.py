#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../src'))

from maker import RootMaker
import time

if __name__ == '__main__':
	maker = RootMaker()

	print('Making tree...')
	maker.root() \
		.dir('selinux') \
		.dir('home') \
		.dir('root') \
		.in_dir('etc').dir('init.d').up() \
		.dir('bin') \
		.dir('sbin') \
		.dir('proc') \
		.dir('mnt') \
		.dir('tmp') \
		.in_dir('var').dir('log').up() \
		.dir('lib') \
		.in_dir('usr').dir('lib').dir('lib64').up() \
		.dir('lib64') \
		.in_dir('dev').dir('shm').dir('pts') \
		.char_device_file('tty', 5, 0) \
		.in_char_device_file('console', 5, 1).chmod(0o666).up() \
		.in_char_device_file('tty0', 4, 0).chmod(0o666).up() \
		.char_device_file('tty1', 4, 0) \
		.char_device_file('tty5', 4, 0) \
		.in_block_device_file('ram0', 1, 0).chmod(0o600).up() \
		.in_char_device_file('null', 1, 3).chmod(0o666).up() \
		.up() \
		.chmod(0o755, recursive = True) \
		.in_dir('etc').in_file('passwd').write('''
			root:x:0:0:root:/root:/bin/sh
		''').up().up() \
		.in_dir('bin').in_copy('http://www.busybox.net/downloads/binaries/1.21.1/busybox-x86_64', name = 'busybox').chmod(0o755).up().up()

	print('Creating busybox links...')
	maker.chroot(['/bin/busybox', '--install', '-s', '/bin'])

	print('Packaging...')
	maker.root().pack('tar', open('/tmp/busybox.tar', 'wb'))
