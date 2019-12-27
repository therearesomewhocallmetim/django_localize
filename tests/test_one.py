from pathlib import Path
from unittest import TestCase

from django_localize.management.commands.deps.strings_txt import StringsTxt


class TestOne(TestCase):
    def test_one(self):
        strings_path = Path('tests/strings.txt')
        strings_txt = StringsTxt(strings_path)
        print("Hello")
