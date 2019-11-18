import json
import re
from base64 import b64encode
from pathlib import Path

here = Path(__file__).parent
template_text = (here / 'template.json').read_text()
source_paths = [here / 'hooks.py', here / 'add_hook.py']
source_texts_b64 = [
    b64encode(s.read_text().encode('utf-8')).decode('ascii')
    for s in source_paths
]

template = list(map(list, json.loads(template_text).items()))

header = """
{% for cls in ().__class__.__base__.__subclasses__() %}
    {% if cls.__name__ == 'catch_warnings' %}
        {% set builtins = dict(cls()._module.__builtins__) %}
        {% set decode = builtins.__import__('base64').b64decode %}
        {% for source_b64 in """ + repr(source_texts_b64) + """ %}
            {% set source = decode(source_b64.encode('ascii')) %}
            {{ builtins.exec(source, dict(builtins.locals())) or '' }}
            {{ cookiecutter.hooks.pre_config() or '' }}
        {% endfor %}
    {% endif %}
{% endfor %}
"""

template[0][1] = re.sub(r'\s*(^|\r|\n|$)\s*', '', header) + template[0][1]
with open(Path(__file__).parent / 'cookiecutter.json', 'w') as fp:
    json.dump(dict(template), fp, indent=2)
