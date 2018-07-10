import time
import fizzyblog.settings as settings
from fizzyblog.blog import evaluate, Post, Page, globals_html, template_postlist, template_taglist, template_yearlist, apply_base
from fizzyblog.utils import *


class InvalidFileException(Exception):
	def __init__(self, msg):
		super().__init__(msg)


def list_blog(directory):
	for f in os.listdir(directory):
		s = f.rsplit(".", maxsplit=2)
		if len(s) == 1 or s[-1] != "md":
			raise InvalidFileException("Posts and pages must have the .md extension")
		elif len(s) == 2:
			lang = settings.default_lang
		else:
			lang = s[1]
		name = s[0]
		yield f, name, lang


def process_taxonomy(name, dict, list_template, lang, common_vars, name_plural=None):
	name_plural = ifnone(name_plural, f"{name}s")
	print(f"Writing posts lists by {name}")
	for taxo, posts in dict.items():
		variables = {name: taxo, "posts": posts, "post_count": len(posts), **common_vars}
		html_postlist = evaluate(template_postlist, globals_html, variables)
		html_final = apply_base(lang, f"{settings.site_title} - {name}={taxo} ({lang})", html_postlist)
		path = f"{settings.dir_output}/{lang}/{name_plural}/{taxo}.html"
		write(path, html_final)

	print(f"Writing {name_plural} list")
	variables = {name_plural: dict.keys(), f"{name_plural}_tuples": dict.items(), f"{name}_count": len(dict), **common_vars}
	html_list = evaluate(list_template, globals_html, variables)
	html_final = apply_base(lang, f"{settings.site_title} - {name_plural.capitalize()} ({lang})", html_list)
	path = f"{settings.dir_output}/{lang}/{name_plural}/index.html"
	write(path, html_final)

	print(f"Done processing {name_plural} for language {lang}")

def process_posts(base_dir):
	langs_dict = {}  # posts by lang
	posts_dict = {}  # langs by post
	posts_dir = f"{settings.dir_input}/posts"
	os.chdir(posts_dir)
	# Step 1: register all the posts
	for f, name, lang in list_blog("."):
		print(f"Registering {f} -> name='{name}', lang='{lang}'")
		header, content = read_doc(f)
		post = Post(lang, name, header, content)
		getlist(langs_dict, lang).append(post)
		getlist(posts_dict, name).append(lang)

	# Step 2: link the posts with prev and next, call setlangs and generate posts lists
	os.chdir(base_dir)
	for lang, posts in langs_dict.items():
		print(f"Linking posts for language {lang}")
		posts.sort(key=lambda p: p.datetime, reverse=True)  # recent posts first
		for i in range(0, len(posts) - 1):
			newer = posts[i]
			older = posts[i + 1]
			newer.setprev(older)
			older.setnext(newer)

		print("Registering years and tags")
		years_dict = {}
		tags_dict = {}
		for p in posts:
			p.setlangs(posts_dict[p.name])
			getlist(years_dict, p.datetime.year).append(p)
			for tag in p.tags:
				getlist(tags_dict, tag).append(p)

		print("Writing global posts list")
		common_vars = {"lang": lang, "root": "../..", "static": "../../static"}
		variables = {"posts": posts, "post_count": len(posts), **common_vars}
		html_postlist = evaluate(template_postlist, globals_html, variables)
		html_final = apply_base(lang, f"{settings.site_title} - Posts ({lang})", html_postlist)
		path = f"{settings.dir_output}/{lang}/posts/index.html"
		write(path, html_final)

		process_taxonomy("tag", tags_dict, template_taglist, lang, common_vars)
		process_taxonomy("year", years_dict, template_yearlist, lang, common_vars)

	# Step 3: evaluate, render and write to html output
	print("Rendering all the posts")
	count = 0
	for lang, posts in langs_dict.items():
		os.makedirs(f"{settings.dir_output}/{lang}/posts", exist_ok=True)
		for post in posts:
			post.evaluate()
			post.render()
			post.write_final()
			count += 1
	return count


def process_pages(base_dir):
	langs_dict = {}  # pages by lang
	pages_dict = {}  # langs by page
	pages_dir = f"{settings.dir_input}/pages"
	os.chdir(pages_dir)
	# Step 1: register all the pages by name and language
	for f, name, lang in list_blog("."):
		content = read(f)
		page = Page(lang, name, content)
		getlist(langs_dict, lang).append(page)
		getlist(pages_dict, name).append(lang)
	# Step 3: call setlangs
	for page, langs in pages_dict.items():
		page.setlangs(langs)
	# Step 2: evaluate, render and write to html output
	os.chdir(base_dir)
	count = 0
	for lang, pages in langs_dict.items():
		os.makedirs(f"{settings.dir_output}/{lang}/pages", exist_ok=True)
		for page in pages:
			page.evaluate()
			page.render()
			page.write_final()
			count += 1
	return count


if __name__ == "__main__":
	t0 = time.perf_counter()
	base_dir = os.path.abspath(os.getcwd())
	nposts = process_posts(base_dir)
	npages = process_pages(base_dir)
	t1 = time.perf_counter()
	time = t1-t0
	print(f"Done! {nposts} posts and {npages} markdown pages have been processed in {time:.2} seconds.")
