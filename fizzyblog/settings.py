import os

import toml
from fizzyblog.utils import touch, create

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

create(f"{dir_input}/templates/post.html", "<article>${post.content}</article>")
create(f"{dir_input}/templates/page.html", "<article>${page.content}</article>")
create(f"{dir_input}/templates/postlist.html", "<div>${ul(posts)}</div>")
create(f"{dir_input}/templates/taglist.html", "<div>${ul(tags)}</div>")
create(f"{dir_input}/templates/yearlist.html", "<div>${ul(years)}</div>")

for lang in site_langs:
	os.makedirs(f"{dir_output}/static", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/posts", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/pages", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/tags", exist_ok=True)
	os.makedirs(f"{dir_output}/{lang}/years", exist_ok=True)
