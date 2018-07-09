import os

import toml

import fizzyblog.default_resources as resources
import fizzyblog.utils as utils

if not os.path.isfile("config.toml"):
	with open("config.toml", "w") as file:
		file.write("[site]")
		file.write("\ntitle = \"My fizzy blog\"")
		file.write("\nauthor = \"me\"")
		file.write("\nlanguages = [\"en\"]")
		file.write("\ndate_format = \"%Y-%m-%d\"")
		file.write("\n\n")
		file.write("[engine]")
		file.write("\ninput = \"src\"")
		file.write("\noutput = \"out\"")
		file.write("\nextensions = [\"markdown.extensions.meta\",\"markdown.extensions.extra\",\"mdx_math\"]")

config = toml.load("config.toml")

# [site]
site_title = config["site"]["title"]
site_author = config["site"]["author"]
site_langs = config["site"]["languages"]
default_lang = site_langs[0]
date_format = config["site"]["date_format"]

# [engine]
dir_input = config["engine"]["input"]
dir_output = config["engine"]["output"]
extensions = config["engine"]["extensions"]

os.makedirs(f"{dir_input}/posts", exist_ok=True)
os.makedirs(f"{dir_input}/pages", exist_ok=True)
os.makedirs(f"{dir_input}/templates", exist_ok=True)

utils.create(f"{dir_input}/templates/base.html", resources.base)
utils.create(f"{dir_input}/templates/head.html", resources.head)
utils.create(f"{dir_input}/templates/post.html", resources.post)
utils.create(f"{dir_input}/templates/page.html", resources.page)
utils.create(f"{dir_input}/templates/post_inlist.html", resources.post_in_list)
utils.create(f"{dir_input}/templates/postlist.html", resources.postlist)
utils.create(f"{dir_input}/templates/taglist.html", resources.taglist)
utils.create(f"{dir_input}/templates/yearlist.html", resources.yearlist)

for lang in site_langs:
	os.makedirs(f"{dir_output}/static", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/posts", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/pages", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/tags", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/years", exist_ok=True)
