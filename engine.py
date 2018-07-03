import re
from typing import Dict, Any, Mapping

import markdown

dir_input = "src"
dir_input_posts = dir_input + "/posts"
dir_input_pages = dir_input + "/pages"
dir_input_static = dir_input + "/static"

dir_output = "out"
dir_output_static = dir_output + "/static"

extensions = ["markdown.extensions.meta",
							"markdown.extensions.extra",
							"mdx_math"]

defaultLang = "en"

__reg = re.compile("\\${.*?}", re.DOTALL)
__markdown = markdown.Markdown(extensions=extensions, output_format="html5")

def evaluate(data: str, globals: Dict[str, Any]=globals(), locals: Mapping[str, Any]=locals()) -> (str, int):
	"""
	Evaluates all the ${expr} and replaces them by their result
	:param data: the data to evaluate
	:param globals: global scope for eval
	:param locals: local scope for eval
	:return: the data with all expressions evaluated
	"""
	return __reg.subn(lambda x: str(eval(x.group()[2:-1], globals, locals)), data)

def render_markdown(md: str) -> str:
	"""
	Renders markdown to HTML
	:param md: the markdown source
	:return: the rendered HTML
	"""
	return __markdown.reset().convert(md)

def read_file(f: str) -> str:
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
	return read_file(f).split("\n---\n", maxsplit=1)
