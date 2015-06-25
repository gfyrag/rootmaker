from .file import File

class SymlinkFile(File):

	def __init__(self, path, target, previous):
		self.target = target
		File.__init__(self, path, previous)