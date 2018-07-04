import datetime
import os

import fizzyblog.blog as blog
import fizzyblog.genhtml as genhtml
import fizzyblog.settings as settings
import fizzyblog.template as template


class InvalidFileException(Exception):
	def __init__(self, msg):
		super().__init__(msg)


def list_blog(directory):
	for f in os.listdir(directory):
		s = f.rsplit(".", max=2)
		if len(s) == 1 or s[-1] != "md":
			raise InvalidFileException("Posts and pages must have the .md extension")
		elif len(s) == 2:
			lang = settings.defaultLang
		else:
			lang = s[1]
		name = s[0]
		yield f, name, lang


def getlist(dict, key):
	v = dict[key]
	if v is None:
		v = []
		dict[key] = v
	return v


def process_posts(base_dir):
	template_postlist = template.read(f"{settings.dir_input}/templates/postlist.html")
	template_taglist = template.read(f"{settings.dir_input}/templates/taglist.html")
	template_yearlist = template.read(f"{settings.dir_input}/templates/yearlist.html")
	langs_dict = {}  # posts by lang
	posts_dict = {}  # langs by post
	posts_dir = f"{settings.dir_input}/posts"
	os.chdir(posts_dir)
	# Step 1: register all the posts
	for f, name, lang in list_blog("."):
		print(f"Registering {f} -> name='{name}', lang='{lang}'")
		header, content = template.read_doc(f)
		post = blog.Post(lang, name, header, content)
		getlist(langs_dict, lang).append(post)
		getlist(posts_dict, name).append(lang)
	# Step 2: link the posts with prev and next, call setlangs and generate posts lists
	for lang, posts in langs_dict:
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
		globscope = {"datetime": datetime, "Post": blog.Post, "Page": blog.Page, **genhtml.__dict__,
								 "template_each": template.template_each}
		variables = {"posts": posts, "lang": lang}
		html_postlist = template.evaluate(template_postlist, globscope, variables)
		path = f"{settings.dir_output}/{lang}/posts/index.html"
		template.write(path, html_postlist)

		print("Writing posts lists by tag")
		for tag, posts in tags_dict:
			variables = {"posts": posts, "tag": tag, "lang": lang}
			html_postlist = template.evaluate(template_postlist, globscope, variables)
			path = f"{settings.dir_output}/{lang}/tags/{tag}.html"
			template.write(path, html_postlist)

		print("Writing tags list")
		variables = {"tags": tags_dict.keys(), "lang": lang}
		html_taglist = template.evaluate(template_taglist, globscope, variables)
		path = f"{settings.dir_output}/{lang}/tags/index.html"
		template.write(path, html_postlist)

		print("Writing posts lists by year")
		for year, posts in years_dict:
			variables = {"posts": posts, "year": year, "lang": lang}
			html_postlist = template.evaluate(template_postlist, globscope, variables)
			path = f"{settings.dir_output}/{lang}/years/{year}.html"
			template.write(path, html_postlist)

		print("Writing years list")
		variables = {"years": years_dict.keys(), "lang": lang}
		html_yearlist = template.evaluate(template_yearlist, globscope, variables)
		path = f"{settings.dir_output}/{lang}/years/index.html"
		template.write(path, html_postlist)

	# Step 3: evaluate, render and write to html output
	print("Rendering all the posts")
	os.chdir(base_dir)
	count = 0
	for lang, posts in langs_dict:
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
		content = template.read(f)
		page = blog.Page(lang, name, content)
		getlist(langs_dict, lang).append(page)
		getlist(pages_dict, name).append(lang)
	# Step 3: call setlangs
	for page, langs in pages_dict:
		page.setlangs(langs)
	# Step 2: evaluate, render and write to html output
	os.chdir(base_dir)
	count = 0
	for lang, pages in langs_dict:
		os.makedirs(f"{settings.dir_output}/{lang}/pages", exist_ok=True)
		for page in pages:
			page.evaluate()
			page.render()
			page.write_final()
			count += 1
	return count


if __name__ == "__main__":
	base_dir = os.path.abspath(os.getcwd())
	nposts = process_posts(base_dir)
	npages = process_pages(base_dir)
	print(f"Done! {nposts} posts and {npages} markdown pages have been processed.")
