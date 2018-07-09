base = ("<!DOCTYPE html>"
				"<html>"
				"<head>"
				"${html_head}"
				"</head>"
				"<body>"
				"${html_body}"
				"</body>"
				"</html>")

head = ("<meta charset=\"utf-8\"/>"
				"<meta name=\"Language\" content=\"${lang}\"/>"
				"<title>${html_title}</title>"
				"<link rel=\"stylesheet\" href=\"${static}/style.css\"/>")

post = ("<article class=\"post\">"
				"<h1>${post.title}</h1>"
				"${post.content}"
				"</article>")

page = ("<article class=\"page\">"
				"${page.content}"
				"</article>")

post_in_list = ("<li class=\"post_in_list\">"
								"<div class=\"title_in_list\">${post.title}</div>"
								"<time datetime=\"${post.datetime.strftime(\"%Y-%m-%d\")}\">"
								"<ul class=\"post_tags\">@{post.tags:tag:<li class=\"tag\">${tag}</li>}</ul>")

postlist = ("<ul class=\"postlist\">"
						"${ftemplate_each(posts, \"post_in_list\", \"post\"}"
						"</ul>")

taglist = ("<ul class=\"taglist\">"
					 "@{tags:tag:<li class=\"tag_in_list\">${tag}</li>}"
					 "</ul>")

yearlist = ("<ul class=\"yearlist\">"
						"@{years:year:<li class=\"year_in_list\">${year}</li>}"
						"</ul>")
