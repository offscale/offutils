"""
Utility functions for offutils
"""

from collections import namedtuple
from operator import methodcaller
from sys import version

from six import string_types

if version[0] == "2":
    iteritems = methodcaller("iteritems")
    itervalues = methodcaller("itervalues")
    iterkeys = methodcaller("iterkeys")
else:
    iteritems = methodcaller("items")
    itervalues = methodcaller("values")
    iterkeys = methodcaller("keys")


def obj_equal_on(obj0, obj1, keys):
    """
    Check if—for key in keys—obj0[key] matches obj1[key]

    :param obj0: First object
    :type obj0: ```dict``

    :param obj1: Second object
    :type obj1: ```dict```

    :param keys: Iterable of keys
    :type keys: ```Iterable[str]```

    :return: Whether they are equal
    :rtype: ```bool```
    """
    for key in keys:
        if obj0.get(key, False) != obj1.get(key):
            return False
    return True


class hashabledict(dict):
    """
    Immutable ```Mapping[str, Any]``
    """

    # From: http://stackoverflow.com/q/1151658
    def __key(self):
        """
        :rtype: ```frozenset```
        """
        return frozenset(self)

    def __hash__(self):
        """
        Return the hash value for the given object.

        :return: hash value
        :rtype: ```int```
        """
        return hash(self.__key())

    def __eq__(self, other):
        """
        Check whether other is equal

        :return: whether other is equal
        :rtype: ```bool```
        """
        return self.__key() == other.__key()


def normalise(idx, obj, keys, obj_id):
    """
    Normalise input obj whence key within.

    :param idx: Index (included verbatim as first param of every entry in the hashabledict)
    :type idx: ```int```

    :param obj: Object to iterate over
    :type obj: ```dict```

    :param keys: Only include these keys from the `obj` in the result
    :type keys: ```collections.abc.Sequence[str]```

    :param obj_id: Object ID (included verbatim as first param of every entry in the hashabledict)
    :type obj_id: ```int```

    :return: Hashable dict mapping key to (idx, id, value)
    :rtype: ```hashabledict[str, NamedTuple('Elem', [('idx', int), ('id', int), ('value', Any)])]```
    """
    return hashabledict(
        (k, namedtuple("Elem", ("idx", "id", "value"))(idx, obj_id, v))
        for k, v in iteritems(obj)
        if k in keys
    )


def l_of_d_intersection(ld0, ld1, keys):
    """Find intersection between a list of dicts and a list of dicts/objects

    :param ld0: List of dictionaries|objects
    :type ld0: ```Union[dict, Any]```

    :param ld1: List of dictionaries
    :type ld1: ```dict```

    :param keys:
    :type keys: List

    :returns intersection of ld0 and ld1 where key is equal. At best, will return `ld0` in full. At worst: [].
    :rtype: ```List[Any]```
    """
    processed_ld0 = frozenset(
        _f
        for _f in (
            normalise(idx_obj[0], idx_obj[1], keys, id(idx_obj[1]))
            for idx_obj in enumerate(ld0)
        )
        if _f
    )
    processed_ld1 = frozenset(
        _f
        for _f in (
            normalise(idx_obj1[0], idx_obj1[1], keys, id(idx_obj1[1]))
            for idx_obj1 in enumerate(ld1)
        )
        if _f
    )

    return [
        ld0[res.idx]
        for result in processed_ld0.intersection(processed_ld1)
        for res in itervalues(result)
    ]


def ensure_separated_str(s_or_l):
    """
    Ensure the input is a str or becomes a space separated string

    :param s_or_l: String or list thereof
    :type s_or_l: ```Union[str,List[str]]```

    :return: `s_or_l` if it's a str otherwise space separated string
    :rtype: ```str``
    """
    return s_or_l if isinstance(s_or_l, string_types) else " ".join(s_or_l)


__all__ = ["ensure_separated_str", "l_of_d_intersection", "normalise", "obj_equal_on"]
