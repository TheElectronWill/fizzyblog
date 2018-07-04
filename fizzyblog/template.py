from typing import Iterable, Dict, Any, Mapping

import re
import markdown
import settings
import datetime
import blog
import genhtml

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

def write(f: str, data: str):
	with open(f, 'w') as file:
		file.write(data)


def template_each(l: Iterable, template_name: str, vname="element") -> str:
	if not template_name.endswith(".html"):
		template_name += ".html"

	template = read(f"{settings.dir_input}/templates/{template_name}")
	globscope = {"datetime": datetime, "Post": blog.Post, "Page": blog.Page, **genhtml.__dict__, "template_each": template_each}
	res = ""
	for e in l:
		variables = {vname: e}
		html, count = evaluate(template, globscope, variables)
		res += html
	return res
