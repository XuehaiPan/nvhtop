# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=disallowed-name,invalid-name

import sys


try:
    if not sys.stdout.isatty():
        raise ImportError
    from termcolor import colored  # pylint: disable=unused-import
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None):  # pylint: disable=unused-argument
        return text


def cut_string(s, maxlen, padstr='...', align='left'):
    assert align in ('left', 'right')

    if not isinstance(s, str):
        s = str(s)

    if len(s) <= maxlen:
        return s
    if align == 'left':
        return s[:maxlen - len(padstr)] + padstr
    return padstr + s[-(maxlen - len(padstr)):]


BLOCK_CHARS = ' ▏▎▍▌▋▊▉'


def make_bar(prefix, percent, width):
    bar = '{}: '.format(prefix)
    if percent != 'N/A':
        if isinstance(percent, str) and percent.endswith('%'):
            percent = percent[:-1]
        percentage = float(percent) / 100.0
        quotient, remainder = divmod(max(1, int(8 * (width - len(bar) - 4) * percentage)), 8)
        bar += '█' * quotient
        if remainder > 0:
            bar += BLOCK_CHARS[remainder]
        bar += ' {:d}%'.format(int(percent)).replace('100%', 'MAX')
    else:
        bar += '░' * (width - len(bar) - 4) + ' N/A'
    return bar.ljust(width)


def bytes2human(x):
    if x == 'N/A':
        return x

    if not isinstance(x, int):
        x = int(x)

    if x < (1 << 10):
        return '{}B'.format(x)
    if x < (1 << 20):
        return '{}KiB'.format(x >> 10)
    return '{}MiB'.format(x >> 20)


def timedelta2human(dt):
    if dt == 'N/A':
        return dt

    if dt.days >= 4:
        return '{:.1f} days'.format(dt.days + dt.seconds / 86400)

    hours, seconds = divmod(86400 * dt.days + dt.seconds, 3600)
    if hours > 0:
        return '{:d}:{:02d}:{:02d}'.format(hours, *divmod(seconds, 60))
    return '{:d}:{:02d}'.format(*divmod(seconds, 60))




class Snapshot(object):
    def __init__(self, real, **items):
        self.real = real
        for key, value in items.items():
            setattr(self, key, value)

    def __bool__(self):
        return bool(self.__dict__)

    def __str__(self):
        keys = set(self.__dict__.keys())
        keys.remove('real')
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join('{}={!r}'.format(key, getattr(self, key)) for key in ['real', *sorted(keys)])
        )

    __repr__ = __str__