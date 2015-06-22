
import tarfile

def pack(path, fileobj):
	with tarfile.open(fileobj = fileobj, mode = 'w') as tar:
		tar.add(path, arcname = '/')

def unpack(path, fileobj):
	with tarfile.open(fileobj = fileobj, mode = 'r') as tar:
		tar.extractall(path)