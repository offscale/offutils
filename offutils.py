#!/usr/bin/env python

# TODO: Move everything from this package to better locations

import socket
import mimetypes
import urllib2

from urlparse import urlsplit, urlunsplit
from types import DictType, NoneType, MethodType, ClassType
from itertools import ifilter, imap, islice
from collections import Counter, namedtuple, deque
from bisect import bisect_left

from pprint import PrettyPrinter

__author__ = 'Samuel Marks'
__version__ = '0.0.3'

pp = PrettyPrinter(indent=4).pprint

unroll_d = lambda d, *keys: (d[key] for key in keys)
obj_to_d = lambda obj: obj if type(obj) is DictType \
    else {k: getattr(obj, k) for k in dir(obj) if not k.startswith('_')}

find_one = lambda key, enumerable, attr: next(ifilter(lambda obj: getattr(obj, attr) == key, enumerable))
find_one.__doc__ == """ @raises `StopIteration` if not found """


def raise_f(exception, *args, **kwargs):
    raise exception(*args, **kwargs)


def http_put(url, payload):
    request = urllib2.Request(url, data=payload)
    request.add_header('Content-Type', mimetypes.types_map['.txt'])
    request.get_method = lambda: 'PUT'
    return urllib2.build_opener(urllib2.HTTPHandler).open(request)


def is_instance_method(obj):
    """Checks if an object is a bound method on an instance."""
    if not isinstance(obj, MethodType):
        return False  # Not a method
    if obj.im_self is None:
        return False  # Method is not bound
    if issubclass(obj.im_class, type) or obj.im_class is ClassType:
        return False  # Method is a classmethod
    return True


# From: http://codereview.stackexchange.com/a/24416
def url_path_join(*parts):
    """Normalize url parts and join them with a slash."""
    schemes, netlocs, paths, queries, fragments = zip(*(urlsplit(part) for part in parts))
    scheme, netloc, query, fragment = first_of_each(schemes, netlocs, queries, fragments)
    path = '/'.join(x.strip('/') for x in paths if x)
    return urlunsplit((scheme, netloc, path, query, fragment))


def first_of_each(*sequences):
    return (next((x for x in sequence if x), '') for sequence in sequences)


def find_by_key(d, key):
    """
        :param d :type DictType
        :param key :type instanceof basestring
    """
    if key in d:
        return d[key]

    for k, v in d.iteritems():
        if type(v) is DictType:
            item = find_by_key(v, key)
            if type(item) is not NoneType:
                return item
    raise ValueError('"{key}" not found'.format(key=key))


def subsequence(many_d):
    """
        :param many_d enumerable containing many :type DictType
        :returns entries which are common between all :type TupleType

        Example:
             >>> ds = {'a': 5, 'b': 6}, {'a': 5}, {'a': 7}
             >>> subsequence(ds)
             >>> ('a;;;5',)
    """
    c = Counter()
    for d in many_d:
        for k, v in d.iteritems():
            c['{0};;;{1}'.format(k, v)] += 0.5
    for k, v in c.iteritems():
        c[k] = int(v)  # Remove all halves, and enable `.elements` to work
    return tuple(c.elements())


find_common_d = lambda target_d, ds: next(
    d for d in ds if any(getattr(d, k) == v for k, v in target_d.iteritems() if k in obj_to_d(d))
)
find_common_d.__doc__ = """ Return first intersecting element between an object/dict and a dict """

l_of_d_intersection = lambda ld0, ld1, keys: tuple(
    elem for elem in ld0
    if ifilter(lambda key: elem.get(key, False) == elem.get(key, None), keys)
)
l_of_d_intersection.__doc__ = """ Find intersection between a list of dicts and a list of dicts/objects

:param ld0 :type [DictType] or :type [AnyObject]
:param ld1 :type [DictType]
:param keys :type ListType

:returns intersection of ld0 and ld1 where key is equal
"""

ping_port = lambda host='localhost', port=2379: (
    lambda s: (lambda res: res or (lambda: (s.close(), True)[1])())(
        s.connect_ex((host, port))
    ))(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
ping_port.__doc__ = """ :returns True on success, [error] number > 0 otherwise """


def percent_overlap(s0, s1):
    if len(s1) > len(s0):
        s0, s1 = s1, s0
    overlap_i = 0.0
    for i in xrange(len(s1)):
        if s0[i] == s1[i]:
            overlap_i += 1
    return overlap_i / len(s1) * 100


def contains(a, x):
    """Return True if the sorted array a contains x."""
    i = bisect_left(a, x)
    return i != len(a) and a[i] == x


def lists_of_dicts_intersection_on_any(keysl, list0, list1):
    return (d for gen in (lists_of_dicts_intersection_on(keys, list0, list1) for keys in keysl)
            for d in gen if d)


def lists_of_dicts_intersection_on(keys, list0, list1):
    """Return an iterable of the dictionaries in list0 that compare equal on
    keys to some dictionary in list1. The dictionaries must have
    sortable values.

    """
    if len(list0) and type(list0[0]) is not DictType:
        _class = type(list0[0]).__name__
        list0 = map(obj_to_d, list0)
    if len(list1) and type(list1[0]) is not DictType:
        _class = type(list1[0]).__name__
        list1 = map(obj_to_d, list1)

    def values(d):
        if 'driver' in d and not isinstance(d['driver'], basestring):
            d['driver_cls'] = d['driver'].__class__
            d['driver'] = d['driver'].__class__.__name__
        try:
            return tuple(d[k] for k in keys)
        except KeyError:
            return None

    values1 = sorted(v for v in map(values, list1) if v is not None)

    return (dict({'_class': _class}, **d) if '_class' in locals() else d
            for d in list0 if contains(values1, values(d)))


class hashabledict(dict):
    # From: http://stackoverflow.com/q/1151658
    def __key(self):
        return frozenset(self)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


def normalise(idx, obj, keys, obj_id):
    '''print 'normalise got'
    print 'idx =', idx
    print 'obj =', obj
    print 'keys =', keys
    print 'obj_id =', obj_id'''
    return hashabledict((k, namedtuple('Elem', 'idx id value')(idx, obj_id, v))
                        for k, v in obj.iteritems() if k in keys)


def l_of_d_intersection(ld0, ld1, keys):
    """ Find intersection between a list of dicts and a list of dicts/objects

    :param ld0 :type [DictType] or :type [AnyObject]
    :param ld1 :type [DictType]
    :param keys :type ListType

    :returns intersection of ld0 and ld1 where key is equal.
                 At best, will return `ld0` in full. At worst: [].
    """
    list0, list1 = ld0, ld1
    if len(list0) and type(list0[0]) is not DictType:
        _class = type(list0[0])
        list0 = map(obj_to_d, list0)
    if len(list1) and type(list1[0]) is not DictType:
        _class = type(list1[0])
        list1 = map(obj_to_d, list1)

    processed_ld0 = frozenset(
        ifilter(None, imap(lambda (idx, obj): normalise(idx, obj, keys, id(obj)),
                           enumerate(list0))))

    processed_ld1 = frozenset(
        ifilter(None, imap(lambda (idx, obj): normalise(idx, obj, keys, id(obj)),
                           enumerate(list1))))

    return (ld0[res.idx]
            for result in processed_ld0.intersection(processed_ld1)
            for res in result.values())


it_consumes = lambda it, n=None: deque(it, maxlen=0) if n is None else next(islice(it, n, n), None)


def update_d(d, arg=None, **kwargs):
    if arg:
        d.update(arg)
    if kwargs:
        d.update(kwargs)
    return d
