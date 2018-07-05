import os

def read(f: str) -> str:
	"""
	Reads a text file to a string
	:param f: the file's path
	:return: the file's content
	"""
	with open(f, 'r') as file:
		return file.read()


def read_doc(f: str) -> (str, str):
	"""
	Reads a document with a header.
	:param f: the file's path
	:return: (header, remaining document)
	"""
	return read(f).split("\n---\n", maxsplit=1)


def touch(path):
	open(path, 'a').close()


def write(f: str, data: str):
	with open(f, 'w+') as file:
		file.write(data)

def create(f: str, data: str = ""):
	if not os.path.isfile(f):
		write(f, data)

def getlist(dict, key):
	v = dict.get(key)
	if v is None:
		v = []
		dict[key] = v
	return v