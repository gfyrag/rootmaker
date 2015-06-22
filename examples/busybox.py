#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../src'))

from maker import RootMaker
import time

if __name__ == '__main__':
	maker = RootMaker()

	print('Making tree...')
	maker.root() \
		.dir('selinux').create().parent() \
		.dir('home').create().parent() \
		.dir('root').create().parent() \
		.dir('etc').create().dir('init.d').create().parent().parent() \
		.dir('bin').create().parent() \
		.dir('sbin').create().parent() \
		.dir('proc').create().parent() \
		.dir('mnt').create().parent() \
		.dir('tmp').create().parent() \
		.dir('var').create().dir('log').create().parent().parent() \
		.dir('lib').create().parent() \
		.dir('usr').create().dir('lib').create().parent().dir('lib64').create().parent().parent() \
		.dir('lib64').create().parent() \
		.dir('dev').create() \
		.char_device_file('tty', 5, 0).create().parent() \
		.char_device_file('console', 5, 1).create().chmod(0o666).parent() \
		.char_device_file('tty0', 4, 0).create().chmod(0o666).parent() \
		.char_device_file('tty1', 4, 0).create().parent() \
		.char_device_file('tty5', 4, 0).create().parent() \
		.block_device_file('ram0', 1, 0).create().chmod(0o600).parent() \
		.char_device_file('null', 1, 3).create().chmod(0o666).parent() \
		.dir('shm').create().parent() \
		.dir('pts').create().parent() \
		.parent() \
		.chmod(0o755, recursive = True) \
		.dir('etc').file('passwd').create().write('''
			root:x:0:0:root:/root:/bin/sh
		''').parent().parent() \
		.dir('bin').copy('http://www.busybox.net/downloads/binaries/1.21.1/busybox-x86_64', name = 'busybox').chmod(0o755).parent().parent()

	print('Creating busybox links...')
	maker.chroot(['/bin/busybox', '--install', '-s', '/bin'])

	print('Packaging...')
	maker.root().pack('tar', open('/tmp/busybox.tar', 'wb'))
