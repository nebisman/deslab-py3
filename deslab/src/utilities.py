"""Common utilities."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

import os
import sys
import shutil
from numbers import Number


def syms(namelst):
    """
    syms takes a string of symbol names separated by
    blanks and converts them to string variables whose
    name is the same that the string contained in such
    variable. It also returns the list of symbols, so it
    can be used as  a, b, c = syms('a b c')
    """
    namelst = str.split(namelst)
    frame = sys._getframe(1)
    for name in namelst:
        frame.f_locals[name] = name
        # inside a function f_locals is only a snapshot, then we
        # also publish the symbols in the globals of the caller
        if frame.f_locals is not frame.f_globals:
            frame.f_globals[name] = name
    del frame
    return namelst


def which(program):
    """
    Determines if the current program is an executable file
    and returns its full path (None if it is not found)
    """
    return shutil.which(program)


def _sortkey(x):
    """
    Key used for sorting states and events of mixed types
    (numbers, strings, tuples and frozensets) in a deterministic
    way. Python 3 does not allow comparisons between different
    types, so we map every object to a comparable tuple.
    """
    if isinstance(x, bool):
        return (0, int(x), '')
    if isinstance(x, Number):
        return (0, x, '')
    if isinstance(x, str):
        return (1, 0, x)
    if isinstance(x, tuple):
        return (2, 0, tuple(_sortkey(i) for i in x))
    if isinstance(x, (frozenset, set)):
        return (3, 0, tuple(sorted(_sortkey(i) for i in x)))
    return (4, 0, str(x))


def _sorted(collection):
    """sorted version of a set of states or events"""
    return sorted(collection, key=_sortkey)


def _tostr(x):
    """string version of a state or event used in default labels"""
    if isinstance(x, tuple):
        return '(' + ','.join(_tostr(i) for i in x) + ')'
    if isinstance(x, (frozenset, set)):
        return r'\{' + ','.join(_tostr(i) for i in _sorted(x)) + r'\}'
    return str(x)
