import template
import genmarkdown
import settings
import datetime

class BlogFile:
  def __init__(self, lang, name, content, parent_dirname):
    self.parent_dirname = parent_dirname
    self.lang = lang
    self.name = name
    self.content = content
    self.url = name + ".html"
    # local scope for exec and eval:
    self.variables = {}
    self.variables["lang"] = self.lang
    self.variables["name"] = self.name
    self.variables["site_title"] = settings.site_title
    self.variables["site_author"] = settings.site_author
    # relative urls:
    self.variables["dir_lang"] = ".."
    self.variables["lang_home"] = "../index.html"
    self.variables["dir_posts"] = "../posts"
    self.variables["dir_tags"] = "../tags"
    self.variables["dir_years"] = "../years"
    self.variables["dir_pages"] = "../pages"
    self.variables["dir_root"] = "../.."
    self.variables["dir_static"] = "../../static"
    self.variables["home"] = "../../index.html"
    # global scope (completed by subclasses):
    self.globscope = {"datetime":datetime, "template_each":template.template_each}
    
  def setlangs(self, langs):
    self.langs = langs
    self.variables["langs"] = langs
    
  def evaluate(self):
    self.content, count = template.evaluate(self.content, self.globscope, self.variables)
    return count
    
  def render(self):
    """Renders the markdown as HTML. This method replaces the 'content' variable."""
    self.content = template.render(self.content)
  
  def write_final(self):
    path = f"{settings.dir_output}/{self.lang}/{self.parent_dirname}/{self.url}"
    with open(path, "w") as file:
      file.write(self.content)

class Post(BlogFile):
  def __init__(self, lang, name, header, content):
    super().__init__(lang, name, content, "posts")
    self.header = header
    # execute the header:
    self.globscope = {**self.globscope, "Post":Post, **genmarkdown.__dict__}
    exec(header, self.globscope, self.variables)
    # calculate datetime:
    self.datetime = datetime.strptime(self.variables["date"], "")
    self.variables["datetime"] = self.datetime
    # ref to important variables:
    self.title = self.variables["title"]
    self.tags = self.variables["tags"]
    assert isinstance(self.title, str)
    assert isinstance(self.tags, list)
  
  def setnext(self, post):
    self.next = post
    self.variables["next"] = post
  
  def setprev(self, post):
    self.prev = post
    self.variables["prev"] = post

class Page(BlogFile):
  def __init__(self, lang, name, content):
    super().__init__(lang, name, content, "pages")
    self.globscope = {**self.globscope, "Page":Page, **genhtml.__dict__}
  

