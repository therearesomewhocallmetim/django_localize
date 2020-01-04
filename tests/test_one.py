from pathlib import Path
from unittest import TestCase

# from django_localizer.management.commands.deps.strings_txt import StringsTxt
from django_localizer.management.commands.generate_localizations import LocalePathProcessor


class TestLocalePathProcessor(TestCase):
    def test_locale_path_processor_one_plural(self):
        strings_path = Path('tests')
        processor = LocalePathProcessor(strings_path)
        l = list(processor.generate_po_file('en'))
        self.assertSequenceEqual(l, ['msgid "string_one"\n', 'msgstr "String one"\n', '\n'])


    def test_locale_path_processor_many_plurals(self):
        strings_path = Path('tests')
        processor = LocalePathProcessor(strings_path)
        l = list(processor.generate_po_file('ru'))
        self.assertSequenceEqual(
            l, [
                'msgid "string_one"\n',
                'msgstr[0] "%s машина стол"\n',
                'msgstr[1] "%s машины стола"\n',
                'msgstr[2] "%s машин столов"\n',
                'msgstr[3] "%s машины столам"\n',
                '\n'])
