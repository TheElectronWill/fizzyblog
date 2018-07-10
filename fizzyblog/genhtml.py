import collections


def ul(l: list, ul_class="", li_class=""):
	return __list_html(l, "ul", ul_class, li_class)


def ol(l: list, ul_class="", li_class=""):
	return __list_html(l, "ol", ul_class, li_class)


def __list_html(l, ltype, ul_class, li_class):
	s = [f"<{ltype} class=\"{ul_class}\">"]
	for elem in l:
		s += f"<li class=\"{li_class}\">{__list_str(elem, ltype)}</li>"
	s += f"</{ltype}>"
	return "".join(s)


def __list_str(elem, ltype):
	if isinstance(elem, collections.Iterable) and not isinstance(elem, str):
		return __list_html(elem, ltype)
	else:
		return str(elem)


def img(url, alt, html_class=""):
	return f"<img class=\"{html_class}\" src=\"{url}\" alt=\"{alt}\">"


def link(url, text, html_class=""):
	return f"<a class=\"{html_class}\" href=\"{url}\">{text}</a>"
