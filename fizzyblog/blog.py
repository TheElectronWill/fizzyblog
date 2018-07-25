from datetime import datetime
from typing import Iterable, Dict, Any, Mapping

import markdown

import fizzyblog.genhtml as genhtml
import fizzyblog.genmarkdown as genmarkdown
import fizzyblog.settings as settings
from fizzyblog.utils import *

__markdown = markdown.Markdown(extensions=settings.extensions, output_format="html5")
flag_let_md_code = True

def __eval(group: str, globals: dict, locals: dict) -> str:
	type = group[0]
	content = group[2:-1]
	if type == '$': # ${expression}
		# Uses eval to evaluates a Python expression, like an addition
		return eval(content, globals, locals)
	elif type == '!': # !{arbitrary code}
		# Puts the code in a function with exec and calls the function to get the result
		# The code should use a return statement to provide the result
		decl = "def __fizzy():\n"
		code = f"{decl}{content}"

		# The local scope won't work because we'll be inside a function.
		# That's why we copy locals to globals
		new_dict = {**globals, **locals}

		exec(code, new_dict, locals) # Execution defines the function __fizzy()
		fizzy = locals.pop("__fizzy") # Get that function
		return fizzy() # Call it to get the result

	elif ":" not in content:  # @{filename}
		if type != '@':
			raise Exception(f"Invalid loop template: {group}")
		template_src = read_ftemplate(content)
		return evaluate(template_src, globals, locals)
	else:
		s = content.split(":", maxsplit=2)
		iterable = eval(s[0], globals, locals)
		if len(s) == 2:  # iterable:code, we name the variable _ (yes! underscore)
			vname = "_"
			exprs = []
			template = s[1]
		else:
			m = s[1].split(";")
			vname = m[0].strip()
			exprs = m[1:]
			template = s[2]

		if type == '§': # §{iterable:vname:template_code}
			return vtemplate_each(iterable, template, vname, exprs, globals, locals)
		else: # @{iterable:vname:filename}
			return ftemplate_each(iterable, template, vname, exprs, globals, locals)

def evaluate(data: str, globals: Dict[str, Any], locals: Mapping[str, Any], let_md_code=flag_let_md_code) -> str:
	"""
	Evaluates all the ${expr}, §{iterable:vname:expr_for_each} and @{iterable:vname:template_file_for_each}
	and replaces them by their result
	:param data: the data to evaluate
	:param globals: global scope for eval
	:param locals: local scope for eval
	:param let_md_code: True to prevent markdown code escapement, False to espace it normally
	:return: the data with all expressions evaluated
	"""
	return braces_replace(data, lambda group: str(__eval(group, globals, locals)), let_md_code)


def render(md: str) -> str:
	"""
	Renders markdown to HTML
	:param md: the markdown source
	:return: the rendered HTML
	"""
	return __markdown.reset().convert(md)


def vtemplate_each(l: Iterable, template_src: str, vname: str, expressions=None, globals=None, locals=None) -> str:
	"""
	Applies a template to each element of l and return the concatenated results.
	:param l: the elements to apply the template to
	:param template_src: the template
	:param vname: the name to give to the element when giving it to the template
	:param expressions: python statements to execute before each template evaluation; the current element is available
	:param globals: the global scope to use
	:param locals: additional local variables
	:return: the concatenated results of all the evaluations of the template
	"""
	expressions = ifnone(expressions, [])
	globals = ifnone(globals, globals_html)
	locals = ifnone(locals, {})
	parts = []
	for e in l:
		if isinstance(e, BlogFile):
			variables = {**locals, vname: e, "lang": e.lang}
		else:
			variables = {**locals, vname: e}
		for expr in expressions:
			exec(expr, globals_html, variables)
		html = evaluate(template_src, globals, variables, flag_let_md_code)
		parts += html
	return "".join(parts)


def ftemplate_each(l: Iterable, template_file: str, vname: str, expressions=None, globals=None, locals=None) -> str:
	"""
	Reads a templates from a file in the templates directory and applies it to each element of l.
	:param l: the elements to apply the template to
	:param template_file: the template's filename; if it doesn't end by ".html" then ".html" will be added automatically
	:param vname: the name to give to the element when giving it to the template
	:param expressions: python statements to execute before each template evaluation; the current element is available
	:param globals: the global scope to use
	:param locals: additional local variables
	:return: the concatenated results of all the evaluations of the template
	"""
	template_src = read_ftemplate(template_file)
	return vtemplate_each(l, template_src, vname, expressions, globals, locals)


def read_ftemplate(name: str) -> str:
	if not name.endswith(".html"):
		name += ".html"

	cached = template_cache.get(name)
	if cached is None:
		cached = read(f"{settings.dir_input}/templates/{name}")
		template_cache[name] = cached
	return cached


def localized_var(lang, var):
	o = settings.config.get("vars")
	if o is None:
		return None

	o = o.get(lang)
	if o is None:
		return settings.config["vars"][settings.default_lang].get(var)

	return ifnone(o.get(var), settings.config["vars"][settings.default_lang].get(var))


current_lang = settings.default_lang
def i18n(var: str, lang=None):
	if lang is None:
		lang = current_lang
	dict = settings.i18n_dict.get(lang)
	if dict is None:
		dict = settings.i18n_dict.get(settings.default_lang)
	if dict is None:
		return None
	else:
		return dict.get(var)

def _(var: str, lang=None):
	return i18n(var, lang)


template_base = read(f"{settings.dir_input}/templates/base.html")
template_post = read(f"{settings.dir_input}/templates/post.html")
template_page = read(f"{settings.dir_input}/templates/page.html")
template_postlist = read(f"{settings.dir_input}/templates/postlist.html")
template_taglist = read(f"{settings.dir_input}/templates/taglist.html")
template_yearlist = read(f"{settings.dir_input}/templates/yearlist.html")
template_cache = {"base.html": template_base,
									"post.html": template_post,
									"postlist.html": template_postlist,
									"taglist.html": template_taglist,
									"yearlist.html": template_yearlist}


def apply_base(current, parent, lang, langs, title, body, vars=None, let_md_code=flag_let_md_code):
	vars = ifnone(vars, common_vars)
	basevars = {**vars, "current": current, "parent": parent, "lang": lang, "langs": langs, "html_title": title, "html_body": body}
	base = evaluate(template_base, globals_html, basevars, let_md_code)
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
		self.content = evaluate(self.content, self.globscope, self.variables)

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
		vars = {"current": self.url,"parent": "posts", "post": self, "lang": self.lang, "langs": self.lang, **common_vars}
		html_body = evaluate(template_post, globals_html, vars)
		html_final = apply_base(self.url, "posts", self.lang, self.langs, f"{settings.site_title} - {self.title}", html_body)
		with open(path, "w") as file:
			file.write(html_final)

	def __str__(self):
		return self.title


class Page(BlogFile):
	def __init__(self, lang, name, content):
		super().__init__(lang, name, content)
		self.globscope = globals_markdown

	def write_final(self):
		path = f"{settings.dir_output}/{self.lang}/pages/{self.url}"
		vars = {"current": self.url, "parent": "pages", "page": self, "lang": self.lang, "langs": self.langs, **common_vars}
		html_body = evaluate(template_page, globals_html, vars)
		html_final = apply_base(self.url, "pages", self.lang, self.langs, f"{settings.site_title} - {self.name}", html_body)
		with open(path, "w") as file:
			file.write(html_final)

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
								 "Page": Page,
								 "i18n": i18n,
								 "_": _}
globals_html = {**globals_basic, **genhtml.__dict__}
globals_markdown = {**globals_basic, **genmarkdown.__dict__}
common_vars = {"root": "../..", "static": "../../static"}
