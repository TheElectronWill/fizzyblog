from datetime import datetime
from typing import Iterable, Dict, Any, Mapping

import markdown

import fizzyblog.genhtml as genhtml
import fizzyblog.genmarkdown as genmarkdown
import fizzyblog.settings as settings
from fizzyblog.utils import *

__markdown = markdown.Markdown(extensions=settings.extensions, output_format="html5")

def __eval(group: str, globals, locals) -> str:
	type = group[0]
	content = group[2:-1]
	if type == '$':
		return eval(content, globals, locals)
	else:
		s = content.split(":", maxsplit=2)
		iterable = eval(s[0], globals, locals)
		vname = s[1]
		template = s[2]
		if type == '@':
			return vtemplate_each(iterable, template, vname)
		else:
			return ftemplate_each(iterable, template, vname)

def evaluate(data: str, globals: Dict[str, Any] = globals(), locals: Mapping[str, Any] = locals()) -> (str, int):
	"""
	Evaluates all the ${expr} and replaces them by their result
	:param data: the data to evaluate
	:param globals: global scope for eval
	:param locals: local scope for eval
	:return: the data with all expressions evaluated
	"""
	return braces_replace(data, lambda group: str(__eval(group, globals, locals)))


def render(md: str) -> str:
	"""
	Renders markdown to HTML
	:param md: the markdown source
	:return: the rendered HTML
	"""
	return __markdown.reset().convert(md)


def vtemplate_each(l: Iterable, template_src: str, vname="element") -> str:
	"""
	Applies a template to each element of l and return the concatenated results.
	:param l: the elements to apply the template to
	:param template_src: the template
	:param vname: the name to give to the element when giving it to the template
	:return: the concatenated results of all the evaluations of the template
	"""
	parts = []
	for e in l:
		variables = {vname: e}
		html, count = evaluate(template_src, globals_html, variables)
		parts += html
	return "".join(parts)


def ftemplate_each(l: Iterable, template_file: str, vname="element") -> str:
	"""
	Reads a templates from a file in the templates directory and applies it to each element of l.
	:param l: the elements to apply the template to
	:param template_file: the template's filename; if it doesn't end by ".html" then ".html" will be added automatically
	:param vname: the name to give to the element when giving it to the template
	:return: the concatenated results of all the evaluations of the template
	"""
	if not template_file.endswith(".html"):
		template_file += ".html"

	template_src = read(f"{settings.dir_input}/templates/{template_file}")
	return vtemplate_each(l, template_src, vname)


template_base = read(f"{settings.dir_input}/templates/base.html")
template_head = read(f"{settings.dir_input}/templates/head.html")
template_post = read(f"{settings.dir_input}/templates/post.html")
template_page = read(f"{settings.dir_input}/templates/page.html")
template_postlist = read(f"{settings.dir_input}/templates/postlist.html")
template_taglist = read(f"{settings.dir_input}/templates/taglist.html")
template_yearlist = read(f"{settings.dir_input}/templates/yearlist.html")


def apply_base(lang, title, body):
	headvars = {"lang": lang, "html_title": title}
	head = evaluate(template_head, globals_html, headvars)

	basevars = {"html_head": head, "html_body": body}
	base = evaluate(template_base, globals_html, basevars)
	return base


class BlogFile:
	def __init__(self, lang, name, content):
		self.lang = lang
		self.name = name
		self.content = content
		self.url = name + ".html"
		# local scope for exec and eval:
		self.variables = {}
		self.variables["lang"] = self.lang
		self.variables["name"] = self.name
		self.variables["site_title"] = settings.site_title
		self.variables["site_author"] = settings.site_author
		# relative urls:
		self.variables["dir_lang"] = ".."
		self.variables["lang_home"] = "../index.html"
		self.variables["dir_posts"] = "../posts"
		self.variables["dir_tags"] = "../tags"
		self.variables["dir_years"] = "../years"
		self.variables["dir_pages"] = "../pages"
		self.variables["dir_root"] = "../.."
		self.variables["dir_static"] = "../../static"
		self.variables["home"] = "../../index.html"
		# global scope (completed by subclasses):
		self.globscope = globals_basic

	def setlangs(self, langs):
		self.langs = langs
		self.variables["langs"] = langs

	def evaluate(self):
		self.content, count = evaluate(self.content, self.globscope, self.variables)
		return count

	def render(self):
		"""Renders the markdown as HTML. This method replaces the 'content' variable."""
		self.content = render(self.content)

	def write_final(self):
		pass

class Post(BlogFile):
	def __init__(self, lang, name, header, content):
		super().__init__(lang, name, content)
		self.header = header
		# execute the header:
		self.globscope = globals_markdown
		exec(header, self.globscope, self.variables)
		# calculate datetime:
		self.datetime = datetime.strptime(self.variables["date"], settings.date_format)
		self.variables["datetime"] = self.datetime
		# ref to important variables:
		self.title = self.variables["title"]
		self.tags = self.variables["tags"]
		assert isinstance(self.title, str)
		assert isinstance(self.tags, list)

	def setnext(self, post):
		self.next = post
		self.variables["next"] = post

	def setprev(self, post):
		self.prev = post
		self.variables["prev"] = post

	def write_final(self):
		path = f"{settings.dir_output}/{self.lang}/posts/{self.url}"
		vars = {"post": self}
		html, c = evaluate(template_post, globals_html, vars)
		with open(path, "w") as file:
			file.write(html)

	def __str__(self):
		return self.title


class Page(BlogFile):
	def __init__(self, lang, name, content):
		super().__init__(lang, name, content)
		self.globscope = globals_markdown

	def write_final(self):
		path = f"{settings.dir_output}/{self.lang}/pages/{self.url}"
		vars = {"page": self}
		html = evaluate(template_page, globals_html, vars)
		with open(path, "w") as file:
			file.write(html)

	def __str__(self):
		return self.name


globals_basic = {"datetime": datetime,
								 "vtemplate_each": vtemplate_each,
								 "ftemplate_each": ftemplate_each,
								 "evaluate": evaluate,
								 "render": render,
								 "settings": settings,
								 "BlogFile": BlogFile,
								 "Post": Post,
								 "Page": Page}
globals_html = {**globals_basic, **genhtml.__dict__}
globals_markdown = {**globals_basic, **genmarkdown.__dict__}