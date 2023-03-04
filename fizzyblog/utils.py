import os
import distutils.dir_util as dirutils


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

def copy_dir(src: str, dest: str):
	dirutils.copy_tree(src, dest)

def remove_dir(dir: str):
	dirutils.remove_tree(dir)
	
def symlink_force(src: str, dst: str):
	is_dir = os.path.isdir(src)
	try:
		os.symlink(src, dst, is_dir)
		print(f"Created link {dst} -> {src}")
	except FileExistsError as e:
		os.remove(dst)
		os.symlink(src, dst, is_dir)
		print(f"Updated link {dst} -> {src}")

def getlist(dict, key):
	v = dict.get(key)
	if v is None:
		v = []
		dict[key] = v
	return v


def braces_replace(data: str, replace_function, let_md_code=False, let_deeply=False) -> str:
	to_eval = "$@§!"
	in_md_code = None

	res = []
	content = []
	count = 0
	i = 0
	limit = len(data)
	while i < limit:
		ch = data[i]
		inext = i + 1
		inext2 = i + 2
		cnext = data[inext] if inext < limit else None
		cnext2 = data[inext2] if inext2 < limit else None

		if let_md_code and (count == 0 or let_deeply):
			if ch == cnext == cnext2 == "`":
				if in_md_code == "```":
					in_md_code = None
				elif in_md_code is None:
					in_md_code = "```"
			elif ch == "`":
				if in_md_code == "`":
					in_md_code = None
				elif in_md_code is None:
					in_md_code = "`"

		if in_md_code is not None:
			res.append(ch)
			i += 1
		else:
			if ch == "\\" and count == 0 and (cnext in to_eval) and cnext2 == "{":
				i += 2
				res.append(cnext)
			elif (ch in to_eval) and cnext == "{":
				count += 1
				i += 2
				content.append(ch)
				content.append(cnext)
			else:
				i += 1
				if count > 0:
					content.append(ch)
					if ch == "{":
						count += 1
					if ch == "}":
						count -= 1
						if count == 0:
							res.append(replace_function("".join(content)))
							content.clear()
				else:
					res.append(ch)

	return "".join(res)

if __name__ == '__main__':
	data = "${in ${inner} @{a:b:c}} @{a${}} }{}{}{}${@{${@{}@{}@{}}}}{}}${ø]]@@@@{]{}{{]}\n"
	r = braces_replace(data, lambda x: "<" + str(x)[2:-1] + ">")
	print(r)

	data = "!{\nstring = f'A string with {variables} inside.'\nstring2 = f'{a}{2}{\"${!{{{_@{}_}}}!}\"}'\n}"
	r = braces_replace(data, lambda x: "<" + str(x)[2:-1] + ">")
	print(r)

	data = """Here is a block of markdown code:
						```java
						public class MyClass {
							private final String test = "${should be included as it is, it isn't an expression}"
						}
						```
						- These should be evaluated: ${expr$} @{expr@} !{expr!}
						- Here is some inline code: `${this isn't an expression either} @{!{}}`
						- These should be evaluated: ${expr$} @{expr@} !{expr!}
						- Escapement: blabla \\${escaped} \\ \\! \\{!{not escaped\\}\\}
					"""
	r = braces_replace(data, lambda x: "<" + str(x)[2:-1] + ">", True)
	print(r)
