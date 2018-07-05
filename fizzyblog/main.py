import os

from fizzyblog.blog import *


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
		variables = {"posts": posts, "lang": lang}
		html_postlist, c = evaluate(template_postlist, globals_html, variables)
		path = f"{settings.dir_output}/{lang}/posts/index.html"
		write(path, html_postlist)

		print("Writing posts lists by tag")
		for tag, posts in tags_dict.items():
			variables = {"posts": posts, "tag": tag, "lang": lang}
			html_postlist, c = evaluate(template_postlist, globals_html, variables)
			path = f"{settings.dir_output}/{lang}/tags/{tag}.html"
			write(path, html_postlist)

		print("Writing tags list")
		variables = {"tags": tags_dict.keys(), "lang": lang}
		html_taglist, c = evaluate(template_taglist, globals_html, variables)
		path = f"{settings.dir_output}/{lang}/tags/index.html"
		write(path, html_taglist)

		print("Writing posts lists by year")
		for year, posts in years_dict.items():
			variables = {"posts": posts, "year": year, "lang": lang}
			html_postlist, c = evaluate(template_postlist, globals_html, variables)
			path = f"{settings.dir_output}/{lang}/years/{year}.html"
			write(path, html_postlist)

		print("Writing years list")
		variables = {"years": years_dict.keys(), "lang": lang}
		html_yearlist, c = evaluate(template_yearlist, globals_html, variables)
		path = f"{settings.dir_output}/{lang}/years/index.html"
		write(path, html_yearlist)

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
	base_dir = os.path.abspath(os.getcwd())
	nposts = process_posts(base_dir)
	npages = process_pages(base_dir)
	print(f"Done! {nposts} posts and {npages} markdown pages have been processed.")
