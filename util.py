from itertools import imap, ifilter
from collections import namedtuple


def obj_equal_on(obj0, obj1, keys):
    for key in keys:
        if obj0.get(key, False) != obj1.get(key, None):
            return False
    return True


class hashabledict(dict):
    # From: http://stackoverflow.com/q/1151658
    def __key(self):
        return frozenset(self)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


def normalise(idx, obj, keys, obj_id):
    return hashabledict((k, namedtuple('Elem', 'idx id value')(idx, obj_id, v))
                        for k, v in obj.iteritems() if k in keys)


def l_of_d_intersection(ld0, ld1, keys):
    """ Find intersection between a list of dicts and a list of dicts/objects

    :param ld0 :type [DictType] or :type [AnyObject]
    :param ld1 :type [DictType]
    :param keys :type ListType

    :returns intersection of ld0 and ld1 where key is equal. At best, will return `ld0` in full. At worst: [].
    """
    processed_ld0 = frozenset(ifilter(None, imap(lambda (idx, obj): normalise(idx, obj, keys, id(obj)), enumerate(ld0))))
    processed_ld1 = frozenset(ifilter(None, imap(lambda (idx, obj): normalise(idx, obj, keys, id(obj)), enumerate(ld1))))

    return [ld0[res.idx] for result in processed_ld0.intersection(processed_ld1) for res in result.values()]


def run_example(ld0, ld1, keys, expected_result):
    result = tuple(l_of_d_intersection(ld0, ld1, keys))
    # print result
    assert result == expected_result, '{0} != {1}'.format(result, expected_result)


def main():
    run_example(
        ld0=[{'foo': 'bar', 'haz': 'more'},
             {'can': 'haz', 'more': 'haz'},
             {'foo': 'jar', 'more': 'fish'}],
        ld1=[{'foo': 'bar'},
             {'can': 'haz'},
             {'foo': 'foo'}],
        keys=('foo',),
        expected_result=({'foo': 'bar', 'haz': 'more'},)
    )

    run_example(
        ld0=[
            {'orange': 'black', 'blue': 'green', 'yellow': 'red'},
            {'blue': 'yellow'},
            {'orange': 'red', 'yellow': 'blue'}
        ],
        ld1=[
            {'orange': 'black', 'yellow': 'red'},
            {'blue': 'yellow'},
            {'orange': 'red', 'yellow': 'blue'}
        ],
        keys=('orange', 'yellow'),
        expected_result=({'orange': 'black', 'blue': 'green', 'yellow': 'red'},
                         {'orange': 'red', 'yellow': 'blue'})
    )


if __name__ == '__main__':
    main()
