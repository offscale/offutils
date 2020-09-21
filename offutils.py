#!/usr/bin/env python

# TODO: Move everything from this package to better locations

import mimetypes
import operator
import socket

from sys import version

if version[0] == "2":
    from itertools import imap as map

from bisect import bisect_left
from collections import Counter, namedtuple, deque, Iterable, OrderedDict
from itertools import islice, takewhile
from os import urandom
from pprint import PrettyPrinter
from random import SystemRandom
from string import ascii_uppercase, digits
from types import MethodType

from functools import reduce

__author__ = "Samuel Marks"
__version__ = "0.0.11"

pp = PrettyPrinter(indent=4).pprint

unroll_d = lambda d, *keys: (d[key] for key in keys)
obj_to_d = (
    lambda obj: obj
    if isinstance(obj, dict)
    else {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_")}
)

find_one = lambda key, enumerable, attr: next(
    obj for obj in enumerable if getattr(obj, attr) == key
)
find_one.__doc__ == """ @raises `StopIteration` if not found """


def raise_f(exception, *args, **kwargs):
    raise exception(*args, **kwargs)


if version[0] == "3":
    import urllib.request, urllib.error, urllib.parse
    from urllib.parse import urlsplit, urlunsplit

    def http_put(url, payload):
        request = urllib.request.Request(url, data=payload)
        request.add_header("Content-Type", mimetypes.types_map[".txt"])
        request.get_method = lambda: "PUT"
        return urllib.request.build_opener(urllib.request.HTTPHandler).open(request)


else:
    import urllib2

    def http_put(url, payload):
        request = urllib2.Request(url, data=payload)
        request.add_header("Content-Type", mimetypes.types_map[".txt"])
        request.get_method = lambda: "PUT"
        return urllib2.build_opener(urllib2.HTTPHandler).open(request)


def is_instance_method(obj):
    """Checks if an object is a bound method on an instance."""
    if not isinstance(obj, MethodType):
        return False  # Not a method
    elif obj.__self__ is None:
        return False  # Method is not bound
    elif (
        issubclass(obj.__self__.__class__, type)
        or hasattr(obj.__self__, "__class__")
        and obj.__self__.__class__
    ):
        return False  # Method is a classmethod
    return True


# From: http://codereview.stackexchange.com/a/24416
def url_path_join(*parts):
    """Normalize url parts and join them with a slash."""
    schemes, netlocs, paths, queries, fragments = list(
        zip(*(urlsplit(part) for part in parts))
    )
    scheme, netloc, query, fragment = first_of_each(
        schemes, netlocs, queries, fragments
    )
    path = "/".join(x.strip("/") for x in paths if x)
    return urlunsplit((scheme, netloc, path, query, fragment))


def first_of_each(*sequences):
    return (next((x for x in sequence if x), "") for sequence in sequences)


def find_by_key(d, key):
    """
    :param d:
    :type d: ```dict```

    :param key:
    :type key: ```str```
    """
    if key in d:
        return d[key]

    for k, v in list(d.items()):
        if isinstance(type(v), dict):
            item = find_by_key(v, key)
            if item is not None:
                return item
    raise ValueError('"{key}" not found'.format(key=key))


def subsequence(many_d):
    """
    :param many_d enumerable containing many :type DictType
    :returns entries which are common between all :type type(tuple)

    Example:
         >>> ds = {'a': 5, 'b': 6}, {'a': 5}, {'a': 7}
         >>> subsequence(ds)
         >>> ('a;;;5',)
    """
    c = Counter()
    for d in many_d:
        for k, v in list(d.items()):
            c["{0};;;{1}".format(k, v)] += 0.5
    for k, v in list(c.items()):
        c[k] = int(v)  # Remove all halves, and enable `.elements` to work
    return tuple(c.elements())


find_common_d = lambda target_d, ds: next(
    d
    for d in ds
    if any(getattr(d, k) == v for k, v in list(target_d.items()) if k in obj_to_d(d))
)
find_common_d.__doc__ = (
    """ Return first intersecting element between an object/dict and a dict """
)

l_of_d_intersection = lambda ld0, ld1, keys: tuple(
    elem
    for elem in ld0
    if [key for key in keys if elem.get(key, False) == elem.get(key, None)]
)
l_of_d_intersection.__doc__ = """ Find intersection between a list of dicts and a list of dicts/objects
:param ld0:
:type ld0: Union[Dict, Any]

:param ld0:
:type ld0: Dict

:param keys:
:type keys: List

:returns intersection of ld0 and ld1 where key is equal
:rtype: List
"""

ping_port = lambda host="localhost", port=2379: (
    lambda s: (lambda res: res or (lambda: (s.close(), True)[1])())(
        s.connect_ex((host, port))
    )
)(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
ping_port.__doc__ = """ :returns True on success, [error] number > 0 otherwise """


def percent_overlap(s0, s1):
    if len(s1) > len(s0):
        s0, s1 = s1, s0
    overlap_i = 0.0
    for i in range(len(s1)):
        if s0[i] == s1[i]:
            overlap_i += 1
    return overlap_i / len(s1) * 100


def contains(a, x):
    """Return True if the sorted array a contains x."""
    i = bisect_left(a, x)
    return i != len(a) and a[i] == x


def lists_of_dicts_intersection_on_any(keysl, list0, list1):
    return (
        d
        for gen in (
            lists_of_dicts_intersection_on(keys, list0, list1) for keys in keysl
        )
        for d in gen
        if d
    )


def lists_of_dicts_intersection_on(keys, list0, list1):
    """Return an iterable of the dictionaries in list0 that compare equal on
    keys to some dictionary in list1. The dictionaries must have
    sortable values.

    """
    if len(list0) and not isinstance(list0[0], dict):
        _class = type(list0[0]).__name__
        list0 = list(map(obj_to_d, list0))
    if len(list1) and not isinstance(list1[0], dict):
        _class = type(list1[0]).__name__
        list1 = list(map(obj_to_d, list1))

    def values(d):
        if "driver" in d and not isinstance(d["driver"], str):
            d["driver_cls"] = d["driver"].__class__
            d["driver"] = d["driver"].__class__.__name__
        try:
            return tuple(d[k] for k in keys)
        except KeyError:
            return None

    values1 = sorted(v for v in map(values, list1) if v is not None)

    return (
        dict({"_class": _class}, **d) if "_class" in locals() else d
        for d in list0
        if contains(values1, values(d))
    )


class hashabledict(dict):
    # From: http://stackoverflow.com/q/1151658
    def __key(self):
        return frozenset(self)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


def normalise(idx, obj, keys, obj_id):
    return hashabledict(
        (k, namedtuple("Elem", "idx id value")(idx, obj_id, v))
        for k, v in list(obj.items())
        if k in keys
    )


def l_of_d_intersection(ld0, ld1, keys):
    """Find intersection between a list of dicts and a list of dicts/objects

    :param ld0:
    :type ld0: Union[Dict, Any]

    :param ld0:
    :type ld0: Dict

    :param keys:
    :type keys: List

    :returns intersection of ld0 and ld1 where key is equal. At best, will return `ld0` in full. At worst: [].
    :rtype: List
    """
    list0, list1 = ld0, ld1
    if len(list0) and not isinstance(list0[0], dict):
        _class = type(list0[0])
        list0 = list(map(obj_to_d, list0))
    if len(list1) and not isinstance(list1[0], dict):
        _class = type(list1[0])
        list1 = list(map(obj_to_d, list1))

    processed_ld0 = frozenset(
        [
            _f
            for _f in [
                normalise(idx_obj[0], idx_obj[1], keys, id(idx_obj[1]))
                for idx_obj in enumerate(list0)
            ]
            if _f
        ]
    )

    processed_ld1 = frozenset(
        [
            _f
            for _f in [
                normalise(idx_obj1[0], idx_obj1[1], keys, id(idx_obj1[1]))
                for idx_obj1 in enumerate(list1)
            ]
            if _f
        ]
    )

    return (
        ld0[res.idx]
        for result in processed_ld0.intersection(processed_ld1)
        for res in list(result.values())
    )


it_consumes = (
    lambda it, n=None: deque(it, maxlen=0)
    if n is None
    else next(islice(it, n, n), None)
)


def update_d(d, arg=None, **kwargs):
    if arg:
        d.update(arg)
    if kwargs:
        d.update(kwargs)
    return d


def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def binary_search(a, x, lo=0, hi=None):
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return pos if pos != hi and a[pos] == x else -1


def validate_conf(conf, required, logger=namedtuple("pp", "error")(pp), name="conf"):
    errors = None
    for k, v in required:
        if k not in conf:
            logger.error(
                "Expected {k} in {name}, something like: {v}".format(
                    name=name, k=k, v=v
                )
            )
            errors = True
    if errors is not None:
        raise ValueError("conf is invalid")


def get_sorted_strnum(iter_of_strnum):
    return sorted(
        (j for j in iter_of_strnum if not j.startswith("_") and str.isdigit(j[-1])),
        key=lambda s: int("".join(takewhile(str.isdigit, s[::-1]))[::-1] or -1),
    )


def filter_strnums(op, val, strnums):
    mapping = {
        ">=": operator.ge,
        "<": operator.lt,
        "=": operator.eq,
        "==": operator.eq,
        "!=": operator.ne,
        "^": operator.xor,
        ">": operator.gt,
        "<=": operator.le,
        "in": operator.contains,
    }  # TODO: There must be a full list somewhere!
    op_f = mapping.get(op) or getattr(operator, op)
    return (
        strnum
        for strnum in strnums
        if op_f(int("".join(takewhile(str.isdigit, strnum[::-1]))[::-1]), int(val))
    )


def add_to(obj, value, dict_typ=OrderedDict, *keys):  # ALPHA version! - TODO: Complete
    if not obj:
        return obj
    elif not keys:
        obj = value
        return obj

    assigned = False
    o = None
    for key in keys:
        if o is not None:
            if key in o:
                o = o[key]
            else:
                o = {key: None}
                assigned = True
        elif key in obj:
            o = obj[key]
        else:
            o = {key: None}
            assigned = True
    if not assigned:
        pass

    return o


is_sequence = lambda arg: (
    not hasattr(arg, "strip")
    and hasattr(arg, "__getitem__")
    or hasattr(arg, "__iter__")
)

EmptyGet = namedtuple("EmptyGet", "get")(lambda: {})

find_replace_many = lambda s, repls: reduce(lambda a, kv: a.replace(*kv), repls, s)

gen_random_str = lambda n: "".join(
    SystemRandom().choice(ascii_uppercase + digits) for _ in range(n)
)


def str_from_file(fname):
    """
    :param fname :type basestring
    :returns content of file :type str
    """
    with open(fname) as f:
        return f.read()


def generate_random_alphanum(length):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(chars[ord(c) % len(chars)] for c in urandom(length))


def ensure_quoted(s, q="'"):
    return (
        "{q}{s}{q}".format(q=q, s=s)
        if isinstance(s, str) and len(s) and s[0] not in ('"', "'")
        else s
    )
