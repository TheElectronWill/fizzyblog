import os

import toml

import fizzyblog.default_resources as resources
import fizzyblog.utils as utils

if not os.path.isfile("config.toml"):
	with open("config.toml", "w") as file:
		file.write((
			'[site]'
	    	'title = "My fizzy blog"'
		    'author = "me"'
		    'languages = ["en"]'
		    'date_format = "%Y-%m-%d"'
		    'max_listed_posts = 8'
		    'max_listed_taxos = 12'
		    ''
		    '[engine]'
		    'input = "src"'
		    'output = "out"'
		    'extensions = ["markdown.extensions.codehilite", "markdown.extensions.extra","mdx_math"]'
		    'symlink_static_resources = true'
		))

config = toml.load("config.toml")

# [site]
_site = config["site"]
site_title = _site["title"]
site_author = _site["author"]
site_langs = _site["languages"]
default_lang = site_langs[0]
date_format = _site["date_format"]
max_listed_posts = _site["max_listed_posts"]
max_listed_taxos = _site["max_listed_taxos"]

# [engine]
_engine = config["engine"]
dir_input = _engine["input"]
dir_output = _engine["output"]
extensions = _engine["extensions"]
symlink_static_resources = _engine["symlink_static_resources"]

os.makedirs(f"{dir_input}/posts", exist_ok=True)
os.makedirs(f"{dir_input}/pages", exist_ok=True)
os.makedirs(f"{dir_input}/templates", exist_ok=True)
os.makedirs(f"{dir_input}/static", exist_ok=True)

utils.create(f"{dir_input}/templates/base.html", resources.base)
utils.create(f"{dir_input}/templates/head.html", resources.head)
utils.create(f"{dir_input}/templates/post.html", resources.post)
utils.create(f"{dir_input}/templates/page.html", resources.page)

utils.create(f"{dir_input}/templates/post_in_list.html", resources.post_in_list)
utils.create(f"{dir_input}/templates/postlist.html", resources.postlist)

utils.create(f"{dir_input}/templates/tag_in_list.html", resources.tag_in_list)
utils.create(f"{dir_input}/templates/taglist.html", resources.taglist)

utils.create(f"{dir_input}/templates/year_in_list.html", resources.year_in_list)
utils.create(f"{dir_input}/templates/yearlist.html", resources.yearlist)

i18n_dict = {}

for lang in site_langs:
	os.makedirs(f"{dir_output}/{lang}/posts", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/pages", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/tags", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/years", exist_ok=True)

	i18n_file = f"{dir_input}/i18n.{lang}.toml"
	if os.path.isfile(i18n_file):
		i18n_dict[lang] = toml.load(i18n_file)

if config.get("i18n") is not None:
	i18n_dict = {**config.get("i18n"), **i18n_dict}
