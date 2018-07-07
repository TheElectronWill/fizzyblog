import collections


def ul(l: list):
	return __list_html(l, "ul")


def ol(l: list):
	return __list_html(l, "ol")


def __list_html(l, ltype):
	s = [f"<{ltype}>"]
	for elem in l:
		s += f"<li>{__list_str(elem, ltype)}</li>"
	s += f"</{ltype}>"
	return "".join(s)


def __list_str(elem, ltype):
	if isinstance(elem, collections.Iterable) and not isinstance(elem, str):
		return __list_html(elem, ltype)
	else:
		return str(elem)


def img(url, alt):
	return f"<img src=\"{url}\" alt=\"{alt}\">"


def link(url, text):
	return f"<a href=\"{url}\">{text}</a>"
