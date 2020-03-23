from os import path
from pathlib import Path

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

from stew.stew import Stew

FORMAT_BY_TAG = {
    'comment': '# {}\n',
    'tags': '# tags: {}\n',
}


class LocalePathProcessor:
    def __init__(self, locale_dir):
        self.all_langs = None
        self.strings_txt = []
        self.warnings = []
        self.locale_dir = locale_dir
        stew_files = self.locale_dir.glob('**/*.stew')
        for stew_file in stew_files:
            if stew_file.is_file():
                self.add_to_process_queue(stew_file)


    def add_to_process_queue(self, filename):
        a_path = self.locale_dir / filename
        if not a_path.exists():
            self.warnings.append(f'File not found: {a_path}')
            return
        self.strings_txt.append(Stew(a_path))


    def process(self):
        self.all_langs = set()
        for st in self.strings_txt:
            self.all_langs.update(st.all_langs)

        self.create_locale_folders()

        self.write_po_files()
        for strings_txt in self.strings_txt:
            strings_txt.write_formatted()
        #     strings_txt.find_spaces_before_punctuation()
        #     strings_txt.find_wrong_paceholders()
        #
        #     self.warnings.extend(strings_txt.warnings)
        #
        for warning in self.warnings:
            print(f'WARNING: {warning}\n\n')


    def write_po_files(self):
        for lang in self.all_langs:
            self.write_one_po_file(lang)


    def write_comment_and_tag(self, str_txt, key):
        for tag, text in str_txt.comments_and_tags.get(key, {}).items():
            yield FORMAT_BY_TAG[tag].format(text)


    def path_for_lang(self, lang):
        if lang == 'comment':
            return
        return self.locale_dir / lang / 'LC_MESSAGES'


    def strip_key(self, key):
        return key.strip('[]').replace('"', '\\"')


    def generate_po_file(self, lang):
        for stew_file in self.strings_txt:
            yield f'\n### from {stew_file.strings_path.relative_to(settings.BASE_DIR)}\n\n'
            for key in stew_file.keys_in_order:
                translations = stew_file.terms.dct.get(key)
                if key not in stew_file.terms.dct:
                    yield f'# {key}\n'
                    continue

                yield from self.write_comment_and_tag(stew_file, key)

                forms = translations.dct.get(lang)
                if not forms:
                    continue

                yield f'msgid "{self.strip_key(key)}"\n'
                if len(forms) == 1:
                    yield f'msgstr "{forms[0]}"\n'
                else:
                    yield f'msgid_plural "{self.strip_key(key)}"\n'
                    for i, form in forms.items():
                        form = form.replace('"', '\\"')
                        yield f'msgstr[{i}] "{form}"\n'
                yield '\n'


    def write_one_po_file(self, lang):
        if not self.path_for_lang(lang).exists():
            return

        with open(self.path_for_lang(lang) / 'django.po', 'w') as outfile:
            outfile.write(PoFileHeader.get_header_for_lang(lang))
            for string in self.generate_po_file(lang):
                outfile.write(string)


    def create_locale_folders(self):
        paths = map(self.path_for_lang, self.all_langs)
        for fpath, lang in zip(paths, self.all_langs):
            if not path.exists(fpath):
                self.warnings.append(
f"""No localization directory exists for language: {lang}. Looking in:
{fpath}

Please, run

        python manage.py makemessages -l {lang}

to create the corresponding folder structure. Please check if there are any special
headers added in the generated .po file and add them to this script.\n
***  FOR NOW THIS LANGUAGE ({lang}) WILL BE IGNORED  ***""")
                # makedirs(fpath)


class Command(BaseCommand):
    help = 'Generate .po and .mo files from .stew files'

    def __init__(self):
        super().__init__(self)
        self.locale_paths = list(map(Path, settings.LOCALE_PATHS))
        app_configs = apps.get_app_configs()
        base_dir = Path(settings.BASE_DIR)

        for app_config in app_configs:
            app_path = Path(app_config.path)
            locale_dir = app_path / 'locale'
            if app_path.parent == base_dir and locale_dir.exists:
                self.locale_paths.append(locale_dir)


    def handle(self, *args, **kwargs):
        for locale_path in self.locale_paths:
            LocalePathProcessor(locale_path).process()
        call_command('compilemessages')


class PoFileHeader:
    @staticmethod
    def get_header_for_lang(lang):
        header = '''# AUTOMATICALLY GENERATED FROM STRINGS.TXT
#
# DO NOT MODIFY THIS FILE MANUALLY!
# To modify translations, add them to the strings.txt file and commit them to git.
# run `
#    python3 manage.py generate_localizations
# `
# And then commit those changes to git.
# To make it clear, the modifications to strings.txt should be committed
# separately, and the modifications to the generated files should also be
# committed separately
#
# , fuzzy
msgid
""
msgstr
""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: \\n"
"PO-Revision-Date: \\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
\n'''.format(lang=lang)

        # Plural forms headers for different languages.
        header += {
            'ru': '''"Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n"
"%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n"
"%100>=11 && n%100<=14)? 2 : 3);\\n"
\n''',
            'pl': '''"Plural-Forms: nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 "
"|| n%100>=20) ? 1 : 2);\\n"\n''',

            'es': '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n',
            'de': '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n',
            'it': '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n',
            'nl': '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n',

            'fr': '"Plural-Forms: nplurals=2; plural=(n > 1);\\n"\n',
            'tr': '"Plural-Forms: nplurals=2; plural=(n > 1);\\n"\n',

        }.get(lang, '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n')
        return header
