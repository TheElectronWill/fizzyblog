# Fizzyblog

OK, I just want a simple blog with articles written in markdown and, very important, with multilingual support, ie I can write an article in several languages. Maybe you want it too? Here is fizzyblog!

## Main features
 
- Uses python-markdown under the hood
- Templates written in html+python
- Admonitions and code hilighting
- Simple tag system
- Can sort articles by year, tag or language
- Ready-to-use default templates, just add your CSS and build your blog :)

## Let's start

### Installation

1. Clone the repository
2. cd to the folder
3. Install the package:

```
python setup.py install
```

### Usage

-> Continue to [the wiki](https://github.com/TheElectronWill/fizzyblog/wiki)

Once you've got your blog, run fizzyblog in your blog's directory.
```sh
python -m fizzyblog 
```

#### Syntax highlighting

For the syntax highlighting to work, you need to define an appropriate CSS style.
According to [the docs](https://python-markdown.github.io/extensions/code_hilite/index.html), this can be done with pygments:

```sh
pygmentize -S default -f html -a .codehilite > code.css
```

Then, you need to make sure that `code.css` is loaded by your webpages.
By default, fizzyblog generate HTML pages that include `/style.css`.
You can edit your `style.css` to import the code stylesheet:
```css
@import "/code.css";
/* add this line at the beginning of the file */
```

Then, update your blog by running fizzyblog.
