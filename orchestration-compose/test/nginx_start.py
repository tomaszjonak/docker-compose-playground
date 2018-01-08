import jinja2
import pathlib


class Worker(object):
    """
    Possible options:
    weight=5
    fail_timeout=5s
    slow_start=30s
    """
    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.options = ' '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])


current_dir = pathlib.Path('.').parent.as_posix()

TEMPLATE_PATH = pathlib.Path(current_dir, 'nginx.conf.template').as_posix()
DESTINATION_PATH = pathlib.Path('/etc/nginx/nginx.conf').as_posix()


env = jinja2.Environment(loader=jinja2.FileSystemLoader(current_dir), trim_blocks=True)

template = env.get_template(TEMPLATE_PATH)
instance = template.render(
    lb_port=80,
    workers=[]
)

pathlib.Path(DESTINATION_PATH).write_text(instance)
