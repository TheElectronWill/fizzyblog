import collections


def ul(l: list):
	return __list_html(l, "ul")


def ol(l: list):
	return __list_html(l, "ol")


def __list_html(l, ltype):
	s = "<%s>" % ltype
	for elem in l:
		s += "<li>%s</li>" % __list_str(elem, ltype)
	s += "</%s>" % ltype
	return s


def __list_str(elem, ltype):
	if isinstance(elem, collections.Iterable):
		return __list_html(elem, ltype)
	else:
		return str(elem)


def img(url, alt):
	return "<img src=\"%s\" alt=\"%s\">" % (url, alt)


def link(url, text):
	return "<a href=\"%s\">%s</a>" % (url, text)
