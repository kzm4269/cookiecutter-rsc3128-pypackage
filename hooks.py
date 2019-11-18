import subprocess
import sys
import shlex
import functools as ft
from pathlib import Path
from subprocess import PIPE

assert sys.version_info >= (3, 5), sys.version

context = locals()['_Context__self']
_cookiecutter = context['cookiecutter']


def run(*args, stdout=PIPE, stderr=PIPE, check=True, **kwargs):
    if isinstance(args[0], str):
        args = [shlex.split(args[0]), *args[1:]]
    try:
        return subprocess.run(
            *args,
            stdout=stdout,
            stderr=stderr,
            check=check,
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise


class Hooks(list):
    def __init__(self, **kwargs):
        self.output_dir = None

    def pre_config(self):
        try:
            run('git', check=False)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            exit(1)

    def package_name(self):
        return 'my_python_package'

    def gitbucket_repository(self):
        return _cookiecutter['package_name'].replace('_', '-')

    def gitbucket_username(self):
        return "L******"

    def shimadzu_email(self):
        return '******@shimadzu.co.jp'

    def package_version(self):
        return '0.0.1'

    def package_description(self):
        return ''

    def pre_gen_project(self):
        _cookiecutter['origin'] = 'http://{}/gitbucket/git/{}/{}.git'.format(
            '172.31.23.128:9080',
            _cookiecutter['gitbucket_username'],
            _cookiecutter['gitbucket_repository'],
        )
        _run = ft.partial(run, cwd=self.output_dir)
        _run('git init')
        _run(
            'git config --local user.name'.split()
            + [_cookiecutter['gitbucket_username']]
        )
        _run(
            'git config --local user.email'.split()
            + [_cookiecutter['shimadzu_email']]
        )
        _run('git remote add origin'.split() + [_cookiecutter['origin']])
        _run('git pull origin master', check=False)

    def post_gen_dir(self, f, args, result):
        if self.output_dir is None:
            self.output_dir = Path(result[0]).absolute()

    def post_gen_file(self, f, args, result):
        pass

    def post_gen_project(self):
        pass


_cookiecutter.update(hooks=Hooks())
