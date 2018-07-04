from typing import Dict, Any, Mapping

import re
import markdown
import settings

__reg = re.compile("\\${.*?}", re.DOTALL)
__markdown = markdown.Markdown(extensions=settings.extensions, output_format="html5")

def evaluate(data: str, globals: Dict[str, Any]=globals(), locals: Mapping[str, Any]=locals()) -> (str, int):
	"""
	Evaluates all the ${expr} and replaces them by their result
	:param data: the data to evaluate
	:param globals: global scope for eval
	:param locals: local scope for eval
	:return: the data with all expressions evaluated
	"""
	return __reg.subn(lambda x: str(eval(x.group()[2:-1], globals, locals)), data)

def render(md: str) -> str:
	"""
	Renders markdown to HTML
	:param md: the markdown source
	:return: the rendered HTML
	"""
	return __markdown.reset().convert(md)

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


