from pathlib import Path
from unittest import TestCase

from django_localizer.management.commands.deps.strings_txt import StringsTxt


class TestOne(TestCase):
    def test_one(self):
        strings_path = Path('tests/strings.txt')
        strings_txt = StringsTxt(strings_path)
        self.assertEqual(len(strings_txt.translations), 1)
        self.assertEqual(len(strings_txt.translations_by_language), 3)

        print("Hello")
