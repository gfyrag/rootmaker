#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../rootmaker'))

from maker import RootMaker
import time

maker = RootMaker()

print('Making tree...')
maker.root() \
	.current_mode(0o755) \
	.dir('selinux') \
	.dir('home') \
	.dir('root') \
	.dir('etc/init.d') \
	.dir('bin') \
	.dir('sbin') \
	.dir('proc') \
	.dir('mnt') \
	.dir('tmp') \
	.dir('var/log') \
	.dir('lib') \
	.dir('usr/lib') \
	.dir('usr/lib64') \
	.dir('lib64') \
	.dir('dev/shm') \
	.dir('dev/pts') \
	.current_mode(0o666) \
	.char_device_file('dev/tty', 5, 0) \
	.char_device_file('dev/console', 5, 1) \
	.char_device_file('dev/tty0', 4, 0) \
	.char_device_file('dev/tty1', 4, 0) \
	.char_device_file('dev/tty5', 4, 0) \
	.block_device_file('dev/ram0', 1, 0) \
	.char_device_file('dev/null', 1, 3) \
	.current_mode(0o755) \
	.in_file('etc/passwd').write('''
		root:x:0:0:root:/root:/bin/sh
	''').up() \
	.in_dir('bin').in_copy('http://www.busybox.net/downloads/binaries/1.21.1/busybox-x86_64', name = 'busybox').up().up()

print('Creating busybox links...')
maker.chroot(['/bin/busybox', '--install', '-s', '/bin'])

print('Packaging...')
maker.root().pack('tar', open('/tmp/busybox.tar', 'wb'))
