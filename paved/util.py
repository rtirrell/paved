# -*- coding: utf-8 -*-
"""paved.util -- helper functions.
"""
import re
from paver.easy import info, options, path, dry, sh

try:
    if not options.virtualenv.activate_cmd:
        raise AttributeError
except AttributeError:
    options.setdotted('virtualenv.activate_cmd', 'source ' + options.paved.cwd / 'source' / 'bin' / 'activate')

from . import paved


__all__ = ['rmFilePatterns', 'rmDirPatterns', 'shv', 'update']


def _walkWithAction(*patterns, **kwargs):
    use_path = path(kwargs.get('use_path', options.paved.cwd))
    action = kwargs.pop('action')
    assert type(action) is str
    assert hasattr(use_path, action)

    use_regex = kwargs.get('use_regex')
    errors = kwargs.get('errors', 'warn')
    walk_method = kwargs.get('walk_method', 'walkfiles')

    for p in patterns:
        info("Looking for %s" % p)
        if use_regex:
            cp = re.compile(p)
            p = None
        for f in getattr(use_path, walk_method)(pattern=p, errors=errors):
            if use_regex and not cp.search(str(f)):
                continue
            if f.exists():
                msg = "%s %s..." % (action, f)
                dry(msg, getattr(f, action))
    

def rmFilePatterns(*patterns, **kwargs):
    """Remove all files under the given path with the given patterns.
    """
    kwargs['action'] = 'remove'
    kwargs['walk_method'] = 'walkfiles'
    return _walkWithAction(*patterns, **kwargs)


def rmDirPatterns(*patterns, **kwargs):
    """Remove all directories under the current path with the given patterns.
    """
    kwargs['action'] = 'rmtree'
    kwargs['walk_method'] = 'walkdirs'
    return _walkWithAction(*patterns, **kwargs)


def shv(command, capture=False, ignore_error=False, cwd=None):
    """Run the given command inside the virtual environment, if available:
    """
    try:
        command = "%s; %s" % (options.virtualenv.activate_cmd, command)
    except AttributeError:
        pass
    return sh(command, capture=capture, ignore_error=ignore_error, cwd=cwd)


def update(dst, src):
    """Recursively update the destination dict-like object with the source dict-like object.

    Useful for merging options and Bunches together!

    Based on:
    http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/#c1
    """
    stack = [(dst, src)]

    def isdict(o):
        return hasattr(o, '__setitem__')

    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if isdict(current_src[key]) and isdict(current_dst[key]):
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst
