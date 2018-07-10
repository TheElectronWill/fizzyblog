base = """
<!DOCTYPE html>
<html>
<head>
${html_head}
</head>
<body>
${html_body}
</body>
</html>
""".strip()

head = """\t<meta charset="utf-8"/>
	<meta name="Language" content="${lang}"/>
	<title>${html_title}</title>
	<link rel="stylesheet" href="${static}/style.css"/>"""

post = """
<article class="post">
<h1>${post.title}</h1>
${post.content}
</article>
""".strip()

page = """
<article class="page">
${page.content}
</article>
""".strip()

post_in_list = """
	<li class="post_in_list">
		<a class="post_link" href="${post.name}.html">${post.title}</a>
		<time datetime="${post.datetime.strftime("%Y-%m-%d")}">
		<ul class="post_tags">§{post.tags:tag:\n\t\t\t<li class="tag">${tag}</li>}
		</ul>
	</li>
"""

postlist = """
<ul class="postlist">
${ftemplate_each(posts, "post_in_list", "post")}
</ul>
""".strip()

tag_in_list = """
	<li class="tag_in_list">
		${link(tag + ".html", tag, "tag_link")}
		<span class="post_count">${post_count}</span>
	</li>
"""

taglist = """
<ul class="taglist">
@{tags_tuples:tuple;tag=tuple[0];post_count=len(tuple[1]):tag_in_list}
</ul>
 """.strip()

year_in_list = """
	<li class="year_in_list">
		${link(str(year) + ".html", year, "year_link")}
		<span class="post_count">${post_count}</span>
	</li>
"""

yearlist = """
<ul class="yearlist">
@{years_tuples:tuple;year=tuple[0];post_count=len(tuple[1]):year_in_list}
</ul>
""".strip()
