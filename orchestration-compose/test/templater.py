import jinja2
import pathlib


class Element(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value


current_dir = pathlib.Path('.').parent.as_posix()

env = jinja2.Environment(loader=jinja2.FileSystemLoader(current_dir), trim_blocks=True)

template = env.get_template('file.template')

instance = template.render(preamble='topkek', elements=[Element('A', 'b'), Element('c', 'd')])

pathlib.Path('file.concrete').write_text(instance)
