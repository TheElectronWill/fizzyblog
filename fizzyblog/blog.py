import re
from datetime import datetime
from typing import Iterable, Dict, Any, Mapping
from fizzyblog.utils import *
import markdown

import fizzyblog.genmarkdown as genmarkdown
import fizzyblog.genhtml as genhtml
import fizzyblog.settings as settings

__reg = re.compile("\\${.*?}", re.DOTALL)
__markdown = markdown.Markdown(extensions=settings.extensions, output_format="html5")

def evaluate(data: str, globals: Dict[str, Any] = globals(), locals: Mapping[str, Any] = locals()) -> (str, int):
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

def template_each(l: Iterable, template_name: str, vname="element") -> str:
	if not template_name.endswith(".html"):
		template_name += ".html"

	template = read(f"{settings.dir_input}/templates/{template_name}")
	res = ""
	for e in l:
		variables = {vname: e}
		html, count = evaluate(template, globals_html, variables)
		res += html
	return res

template_post = read(f"{settings.dir_input}/templates/post.html")
template_page = read(f"{settings.dir_input}/templates/page.html")
template_postlist = read(f"{settings.dir_input}/templates/postlist.html")
template_taglist = read(f"{settings.dir_input}/templates/taglist.html")
template_yearlist = read(f"{settings.dir_input}/templates/yearlist.html")

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
								 "template_each": template_each,
								 "evaluate": evaluate,
								 "render": render,
								 "settings": settings,
								 "BlogFile": BlogFile,
								 "Post": Post,
								 "Page": Page}
globals_html = {**globals_basic, **genhtml.__dict__}
globals_markdown = {**globals_basic, **genmarkdown.__dict__}