from unittest import TestCase, main as unittest_main

from offutils import lists_of_dicts_intersection_on, it_consumes


class TestListOfDictsIntersectionOn(TestCase):
    def test_simple(self):
        l0 = [{'foo': 5, 'bar': 'foobar', 'can': 5}]
        l1 = [{'foo': 5, 'bar': 'foobar', 'can': 6}]

        r0 = tuple(lists_of_dicts_intersection_on(('foo', 'bar'), l0, l1))
        self.assertGreater(len(r0), 0, 'r0 is empty')
        it_consumes(all((self.assertEqual(obj['foo'], l1[idx]['foo']),
                         self.assertEqual(obj['bar'], l1[idx]['bar'])))
                    for idx, obj in enumerate(r0))

        r1 = tuple(lists_of_dicts_intersection_on(('foo', 'can'), l0, l1))
        self.assertEqual(len(r1), 0, 'r1 is not empty')

    def test_complex(self):
        l0 = [{'foo': 5e5, 'can': u'haz', 'bar': [{'alpha': 'a'}]}]
        l1 = [{'foo': 5e5, 'can': u'haz', 'bar': [{'alpha': 'b'}]}]
        l2 = [{'foo': 5e6, 'can': u'haz', 'bar': [{'alpha': 'b'}]}]

        r0 = tuple(lists_of_dicts_intersection_on(('foo', 'bar'), l0, l1))
        self.assertEqual(len(r0), 0, 'r0 is not empty')

        r1 = tuple(lists_of_dicts_intersection_on(('foo', 'can'), l0, l1))
        self.assertGreater(len(r1), 0, 'r1 is empty')
        it_consumes(self.assertDictEqual(obj, l0[idx])
                    for idx, obj in enumerate(r1))

        r2 = tuple(lists_of_dicts_intersection_on(('can', 'bar'), l1, l2))
        self.assertGreater(len(r2), 0, 'r2 is empty')
        it_consumes(all((self.assertEqual(obj['can'], l2[idx]['can']),
                         self.assertEqual(obj['bar'], l2[idx]['bar'])))
                    for idx, obj in enumerate(r2))

    def test_real(self):
        options = [{'availability_zone': {u'name': u'ap-southeast-2a', u'zone_state': u'available',
                                          u'region_name': u'ap-southeast-2'}, 'name': u'ap-southeast-2',
                    'region_name': u'ap-southeast-2'}]
        enumerable = [
            {'country': 'Australia',
             'availability_zone': {'name': 'ap-southeast-2a', 'zone_state': 'available',
                                   'region_name': 'ap-southeast-2'},
             'driver': 'EC2NodeDriver', 'id': '0', 'name': 'ap-southeast-2a'}, {'country': 'Australia',
                                                                                'availability_zone': {
                                                                                    'name': 'ap-southeast-2b',
                                                                                    'zone_state': 'available',
                                                                                    'region_name': 'ap-southeast-2'},
                                                                                'driver': 'EC2NodeDriver',
                                                                                'id': '1',
                                                                                'name': 'ap-southeast-2b'},
            {'country': 'Australia', 'availability_zone': {'name': 'ap-southeast-2c', 'zone_state': 'available',
                                                           'region_name': 'ap-southeast-2'},
             'driver': 'EC2NodeDriver', 'id': '2', 'name': 'ap-southeast-2c'}]

        self.assertDictEqual(enumerable[0]['availability_zone'], options[0]['availability_zone'])

        intersect = tuple(lists_of_dicts_intersection_on(('availability_zone',), enumerable, options))
        self.assertGreater(len(intersect), 0, 'intersect is empty')
        it_consumes(self.assertEqual(obj['availability_zone'], options[idx]['availability_zone'])
                    for idx, obj in enumerate(intersect))


if __name__ == '__main__':
    unittest_main()
