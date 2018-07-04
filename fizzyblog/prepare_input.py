import os

import fizzyblog.settings as settings


def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path)


def touch(path):
	with open(path, 'a'):
		os.utime(path, None)


if __name__ == "__main__":
	wd = os.getcwd()
	mkdir(settings.dir_input)
	os.chdir(settings.dir_input)

	mkdir("posts")
	touch("posts/hello.md")
	touch("posts/test.md")

	mkdir("pages")
	touch("pages/about.md")

	mkdir("templates")
	touch("templates/list_tags.html")
	touch("templates/list_posts.html")
	touch("templates/post.html")

	mkdir("static")
	touch("static/favicon.png")

	chdir(wd)
	mkdir(settings.dir_output)
	chdir(settings.dir_output)
	print("Input directory is ready: " + os.path.abspath(settings.dir_input))
