from unittest import TestCase

from launcher.mods.info import ModInfo


class ModInfoTestCase(TestCase):

    _url: str = 'https://somewhere/on/the/internet'

    _iurl: str = 'https://also/on/the/internet'

    _full_dataset: dict = {
        'author': 'mario', 'name': 'modname',
        'title': '999- modname',
        'url': _url, 'iurl': _iurl,
        'subdirs': ['foobar'], 'args': ('filename', 'HASH')
    }

    _partial_data1: dict = {
        'name': 'separator'
    }

    _partial_data2: dict = {
        'url': _url,
        'iurl': _iurl,
        'subdirs': ['foo', 'bar']
    }

    def test_full_dataset(self):
        m = ModInfo(self._full_dataset)

        self.assertEqual(m.author, 'mario')
        self.assertEqual(m.name, 'modname')
        self.assertEqual(m.title, '999- modname')
        self.assertEqual(m.url, self._url)
        self.assertEqual(m.iurl, self._iurl)
        self.assertEqual(
            len(m.subdirs), len(self._full_dataset['subdirs']),
            'Invalid number of subdirs'
        )
        self.assertEqual(m.subdirs[0], 'foobar', 'Invalid subdir')
        self.assertEqual(m.args, ('filename', 'HASH'))

    def test_partial_data1(self):
        m = ModInfo(self._partial_data1)

        self.assertEqual(m.name, 'separator')
        self.assertEqual(m.author, '')
        self.assertEqual(m.title, '')
        self.assertEqual(m.url, '')
        self.assertEqual(m.iurl, '')
        self.assertEqual(m.subdirs, None)
        self.assertEqual(m.args, None)

    def test_partial_data2(self):
        m = ModInfo(self._partial_data2)

        self.assertEqual(m.name, '')
        self.assertEqual(m.author, '')
        self.assertEqual(m.title, '')
        self.assertEqual(m.url, self._url)
        self.assertEqual(m.iurl, self._iurl)
        self.assertEqual(
            len(m.subdirs), len(self._partial_data2['subdirs']),
            'Invalid number of subdirs'
        )
        self.assertIn('foo', self._partial_data2['subdirs'])
        self.assertIn('bar', self._partial_data2['subdirs'])
        self.assertEqual(m.args, None)

    def test_set_name(self):
        m = ModInfo(self._partial_data1)
        new_name = '1337'

        self.assertEqual(m.name, 'separator', 'Invalid name before set')

        m.name = new_name
        self.assertEqual(m.name, new_name, 'Invalid name after set')
