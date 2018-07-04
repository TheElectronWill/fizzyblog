import toml
import os.path
if not os.path.isfile("config.toml"):
  with open("config.toml", "w") as file:
    file.write("[site]")
    file.write("title = \"My fizzy blog\"")
    file.write("author = \"me\"")
    file.write("languages = [\"en\"]")
    file.write("")
    file.write("[engine]")
    file.write("input = \"src\"")
    file.write("output = \"out\"")
    file.write("extensions = [\"markdown.extensions.meta\",\"markdown.extensions.extra\",\"mdx_math\"]")

config = toml.load("config.toml")

# [site]
site_title = config["site"]["title"]
site_author = config["site"]["author"]
site_langs = config["site"]["languages"]
defaultLang = site_langs[0]

# [engine]
dir_input = config["engine"]["input"]
dir_output = config["engine"]["output"]
extensions = config["engine"]["extensions"]

