import settings
import template
import blog
import os

class InvalidFileException(Exception):
  def __init__(self, msg):
    super().__init__(msg)
    
def list_blog(directory):
  for f in os.listdir(directory):
    s = f.rsplit(".", max=2)
    if len(s) == 1 or s[-1] != "md":
      raise InvalidFileException("Posts and pages must have the .md extension")
    else if len(s) == 2:
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
  langs_dict = {} # posts by lang
  posts_dict = {} # langs by post
  posts_dir = f"{settings.dir_input}/posts"
  os.chdir(posts_dir)
  # Step 1: register all the posts by name and language
  for f, name, lang in list_blog("."):
    header, content = template.read_doc(f)
    post = blog.Post(lang, name, header, content)
    getlist(langs_dict, lang).append(post)
    getlist(posts_dict, name).append(lang)
  # Step 2: link the posts with prev and next, and call setlangs
  for lang, posts in langs_dict:
    posts.sort(key=lambda p: p.datetime, reverse=True)
    for i in range(0, len(posts)-1):
      newer = posts[i]
      older = posts[i+1]
      newer.setprev(older)
      older.setnext(newer)
      newer.setlangs(posts_dict[newer.name])
  # Step 3: evaluate, render and write to html output
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
  langs_dict = {} # pages by lang
  pages_dict = {} # langs by page
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
 
