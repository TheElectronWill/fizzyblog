import os
from typing import Iterator


def ifnone(v, default):
	if v is None:
		return default
	else:
		return v

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

__types = "$@§"

def braces_iter(data: str) -> Iterator[str]:
	content = []
	count = 0
	i = 0
	limit = len(data)
	while i < limit:
		ch = data[i]
		inext = i + 1
		cnext = data[inext] if inext < limit else None
		if ch == "\\" and count == 0 and (cnext in __types):
			i += 2
		if (ch in __types) and cnext == "{":
			count += 1
			i += 2
			content.append(ch)
			content.append(cnext)
		else:
			i += 1
			if count > 0:
				content.append(ch)
			if ch == "}":
				count -= 1
				if count == 0:
					yield "".join(content)
					content.clear()


def braces_replace(data: str, replacer) -> str:
	res = []
	content = []
	count = 0
	i = 0
	limit = len(data)
	while i < limit:
		ch = data[i]
		inext = i + 1
		cnext = data[inext] if inext < limit else None
		if ch == "\\" and count == 0 and (cnext in __types):
			i += 2
		if (ch in __types) and cnext == "{":
			count += 1
			i += 2
			content.append(ch)
			content.append(cnext)
		else:
			i += 1
			if count > 0:
				content.append(ch)
				if ch == "}":
					count -= 1
					if count == 0:
						res.append(replacer("".join(content)))
						content.clear()
			else:
				res.append(ch)
	return "".join(res)

if __name__ == '__main__':
	data = "${in ${inner} @{a:b:c}} @{a${}} }{}{}{}${@{${@{}@{}@{}}}}{}}${ø]]@@@@{]{}{{]}\n"*100
	r = braces_replace(data, lambda x: "'" + str(x)[2:-1] + "'")
	print(r)