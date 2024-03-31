# -*- coding: utf-8 -*-
"""
Test utility functions from util.py
"""

from collections import OrderedDict, defaultdict
from copy import deepcopy
from unittest import TestCase
from unittest import main as unittest_main

from offutils import (
    add_to,
    binary_search,
    it_consumes,
    l_of_d_intersection,
    lists_of_dicts_intersection_on,
    lists_of_dicts_intersection_on_any,
)


class TestListOfDictsIntersectionOn(TestCase):
    def test_simple(self):
        l0 = [{"foo": 5, "bar": "foobar", "can": 5}]
        l1 = [{"foo": 5, "bar": "foobar", "can": 6}]

        r0 = tuple(lists_of_dicts_intersection_on(("foo", "bar"), l0, l1))
        self.assertGreater(len(r0), 0, "r0 is empty")
        it_consumes(
            all(
                (
                    self.assertEqual(obj["foo"], l1[idx]["foo"]),
                    self.assertEqual(obj["bar"], l1[idx]["bar"]),
                )
            )
            for idx, obj in enumerate(r0)
        )

        r1 = tuple(lists_of_dicts_intersection_on(("foo", "can"), l0, l1))
        self.assertEqual(len(r1), 0, "r1 is not empty")

    def test_complex(self):
        l0 = [{"foo": 5e5, "can": "haz", "bar": [{"alpha": "a"}]}]
        l1 = [{"foo": 5e5, "can": "haz", "bar": [{"alpha": "b"}]}]
        l2 = [{"foo": 5e6, "can": "haz", "bar": [{"alpha": "b"}]}]

        r0 = tuple(lists_of_dicts_intersection_on(("foo", "bar"), l0, l1))
        self.assertEqual(len(r0), 0, "r0 is not empty")

        r1 = tuple(lists_of_dicts_intersection_on(("foo", "can"), l0, l1))
        self.assertGreater(len(r1), 0, "r1 is empty")
        it_consumes(
            all(
                (
                    self.assertEqual(obj["foo"], l1[idx]["foo"]),
                    self.assertEqual(obj["can"], l1[idx]["can"]),
                )
            )
            for idx, obj in enumerate(r1)
        )

        r2 = tuple(lists_of_dicts_intersection_on(("can", "bar"), l1, l2))
        self.assertGreater(len(r2), 0, "r2 is empty")
        it_consumes(
            all(
                (
                    self.assertEqual(obj["can"], l2[idx]["can"]),
                    self.assertEqual(obj["bar"], l2[idx]["bar"]),
                )
            )
            for idx, obj in enumerate(r2)
        )

        r3 = next(
            lists_of_dicts_intersection_on_any((("foo", "bar"), ("foo", "can")), l0, l1)
        )

        self.assertIsNotNone(r3, "r3 is None")
        it_consumes(
            all(
                (
                    self.assertEqual(obj["foo"], l1[idx]["foo"]),
                    self.assertEqual(obj["can"], l1[idx]["can"]),
                )
            )
            for idx, obj in enumerate([r3])
        )

    def test_real(self):
        options = [
            {
                "availability_zone": {
                    "name": "ap-southeast-2a",
                    "zone_state": "available",
                    "region_name": "ap-southeast-2",
                },
                "name": "ap-southeast-2",
                "region_name": "ap-southeast-2",
            }
        ]
        enumerable = [
            {
                "country": "Australia",
                "availability_zone": {
                    "name": "ap-southeast-2a",
                    "zone_state": "available",
                    "region_name": "ap-southeast-2",
                },
                "driver": "EC2NodeDriver",
                "id": "0",
                "name": "ap-southeast-2a",
            },
            {
                "country": "Australia",
                "availability_zone": {
                    "name": "ap-southeast-2b",
                    "zone_state": "available",
                    "region_name": "ap-southeast-2",
                },
                "driver": "EC2NodeDriver",
                "id": "1",
                "name": "ap-southeast-2b",
            },
            {
                "country": "Australia",
                "availability_zone": {
                    "name": "ap-southeast-2c",
                    "zone_state": "available",
                    "region_name": "ap-southeast-2",
                },
                "driver": "EC2NodeDriver",
                "id": "2",
                "name": "ap-southeast-2c",
            },
        ]

        self.assertDictEqual(
            enumerable[0]["availability_zone"], options[0]["availability_zone"]
        )

        intersect = tuple(
            lists_of_dicts_intersection_on(("availability_zone",), enumerable, options)
        )
        self.assertGreater(len(intersect), 0, "intersect is empty")
        it_consumes(
            self.assertEqual(
                obj["availability_zone"], options[idx]["availability_zone"]
            )
            for idx, obj in enumerate(intersect)
        )


class TestBinarySearch(TestCase):
    a = tuple(range(10))

    def test_binary_search(self):
        self.assertTrue(binary_search(self.a, 5))
        self.assertEqual(binary_search(self.a, 15), -1)


class TestAddTo(TestCase):
    """
    ds = (
        ,
        {'foo': {'bar': None}},
        {'foo': None},
        None
    )
    """

    def test_add_to(self):
        l = lambda: defaultdict(l)
        table = l()

        table[0][1][2][3][4][5] = 6

        val = {"c": 7}

        d0 = {"foo": {"bar": {"can": {"haz": OrderedDict({"a": 5, "b": 6})}}}}
        e0 = deepcopy(d0)
        e0["foo"]["bar"]["can"]["haz"]["c"] = val["c"]
        print(("d0 =", d0))
        print(("e0 =", e0))
        print(
            (
                "add_to(d0, val, OrderedDict, 'foo', 'bar', 'can', 'haz') =",
                add_to(d0, val, OrderedDict, "foo", "bar", "can", "haz"),
            )
        )
        self.assertDictEqual(
            add_to(d0, val, OrderedDict, "foo", "bar", "can", "haz"), e0
        )
        self.assertDictEqual(d0, e0)


def run_example(ld0, ld1, keys, expected_result):
    result = tuple(l_of_d_intersection(ld0, ld1, keys))
    # print result
    assert result == expected_result, "{} != {}".format(result, expected_result)


def main():
    run_example(
        ld0=[
            {"foo": "bar", "haz": "more"},
            {"can": "haz", "more": "haz"},
            {"foo": "jar", "more": "fish"},
        ],
        ld1=[{"foo": "bar"}, {"can": "haz"}, {"foo": "foo"}],
        keys=("foo",),
        expected_result=({"foo": "bar", "haz": "more"},),
    )

    run_example(
        ld0=[
            {"orange": "black", "blue": "green", "yellow": "red"},
            {"blue": "yellow"},
            {"orange": "red", "yellow": "blue"},
        ],
        ld1=[
            {"orange": "black", "yellow": "red"},
            {"blue": "yellow"},
            {"orange": "red", "yellow": "blue"},
        ],
        keys=("orange", "yellow"),
        expected_result=(
            {"orange": "black", "blue": "green", "yellow": "red"},
            {"orange": "red", "yellow": "blue"},
        ),
    )


if __name__ == "__main__":
    unittest_main()
