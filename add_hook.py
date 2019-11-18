import sys

import cookiecutter
assert sys.version_info >= (3, 5), sys.version


def overwrite_func(orig, new, signature=None):
    """https://qiita.com/kzm4269/items/6a120fb7832467e61734"""
    import inspect
    from types import FunctionType
    from textwrap import dedent
    assert isinstance(orig, FunctionType), (orig, type(orig))
    assert isinstance(new, FunctionType), (new, type(new))
    if signature is None:
        signature = inspect.signature(orig)
    params = [
        (str(p).split(':')[0].split('=')[0], p)
        for k, p in signature.parameters.items()
        if k != '__overwrite_func'
    ]
    default = {p.name: p.default for _, p in params}
    anno = {p.name: p.annotation for _, p in params}
    args_kwargs = [
        k if k[0] == '*' or p.kind == p.POSITIONAL_ONLY else k + '=' + k
        for k, p in params
    ]
    signature_ = [
        (k + (':anno["' + k + '"]' if p.annotation != p.empty else '')
         + ('=default["' + k + '"]' if p.default != p.empty else ''),
         not (p.kind == p.VAR_KEYWORD or p.kind == p.KEYWORD_ONLY))
        for k, p in params
    ]
    signature__ = [s for s, positional in signature_ if positional]
    signature__.append('__overwrite_func=new')
    signature__.extend(s for s, positional in signature_ if not positional)
    signature__ = '(' + ', '.join(signature__) + ')'
    if signature.return_annotation is not inspect.Signature.empty:
        anno['return'] = signature.return_annotation
        signature__ += ' -> anno["return"]'
    source = dedent("""
    def outer():
        """ + '='.join(list(orig.__code__.co_freevars) + ['None']) + """
        def inner""" + signature__ + """:
            """ + ', '.join(orig.__code__.co_freevars) + """
            return __overwrite_func(""" + ', '.join(args_kwargs) + """)
        return inner
    """)
    globals_ = {}
    exec(source, dict(new=new, default=default, anno=anno), globals_)
    inner = globals_['outer']()
    globals_.clear()
    orig.__code__ = inner.__code__
    orig.__defaults__ = inner.__defaults__
    orig.__kwdefaults__ = inner.__kwdefaults__
    orig.__annotations__ = inner.__annotations__


def copy_func(f):
    """https://stackoverflow.com/questions/13503079"""
    import functools
    import types
    assert isinstance(f, types.FunctionType), (f, type(f))
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g.__kwdefaults__ = f.__kwdefaults__
    functools.update_wrapper(g, f)
    return g


def add_hook(func, pre_call=None, post_call=None, except_=None, finally_=None):
    """https://qiita.com/kzm4269/items/6a120fb7832467e61734"""
    import inspect
    func_sig = inspect.signature(func)
    func_copy = copy_func(func)

    def hook(*args, **kwargs):
        bound_args = func_sig.bind(*args, **kwargs)
        if pre_call is not None:
            pre_call(func_copy, bound_args)
        try:
            return_ = func_copy(*args, **kwargs)
        except BaseException as e:
            if except_ is not None:
                except_(func_copy, bound_args, e)
            raise
        else:
            if post_call is not None:
                post_call(func_copy, bound_args, return_)
        finally:
            if finally_ is not None:
                finally_(func_copy, bound_args)
        return return_

    overwrite_func(func, hook)


context = locals()['_Context__self']
_cookiecutter = context['cookiecutter']

add_hook(
    cookiecutter.generate.render_and_create_dir,
    post_call=getattr(_cookiecutter['hooks'], 'post_gen_dir', None),
)
add_hook(
    cookiecutter.generate.generate_file,
    post_call=getattr(_cookiecutter['hooks'], 'post_gen_file', None),
)
