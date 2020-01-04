from os import path
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

from stew.stew import Stew

FORMAT_BY_TAG = {
    "comment": "# {}\n",
    "tags": "# tags: {}\n",
}


class LocalePathProcessor:
    def __init__(self, locale_dir):
        self.all_langs = None
        self.strings_txt = []
        self.warnings = []
        self.locale_dir = locale_dir
        self.add_to_process_queue("strings.stew")


    def add_to_process_queue(self, filename):
        a_path = self.locale_dir / filename
        if not a_path.exists():
            self.warnings.append("File not found: {}".format(a_path))
            return
        self.strings_txt.append(Stew(a_path))


    def process(self):
        self.all_langs = set()
        for st in self.strings_txt:
            self.all_langs.update(st.all_langs)

        self.create_locale_folders()

        self.write_po_files()
        # for strings_txt in self.strings_txt:
        #     strings_txt.write_formatted()
        #     strings_txt.find_spaces_before_punctuation()
        #     strings_txt.find_wrong_paceholders()
        #
        #     self.warnings.extend(strings_txt.warnings)
        #
        # for warning in self.warnings:
        #     print("WARNING: {}\n\n".format(warning))


    def write_po_files(self):
        for lang in self.all_langs:
            self.write_one_po_file(lang)


    def write_comment_and_tag(self, str_txt, key, outfile):
        for tag, text in str_txt.comments_and_tags.get(key, {}).items():
            outfile.write(FORMAT_BY_TAG[tag].format(text))


    def path_for_lang(self, lang):
        if lang == "comment":
            return
        return self.locale_dir / lang / "LC_MESSAGES"


    def strip_key(self, key):
        return key.strip("[]")


    def generate_po_file(self, lang):
        # Add the lang-specific header
        for stew_file in self.strings_txt:
            for term, translations in stew_file.terms.items():
                forms = translations.dct.get(lang)
                if not forms:
                    continue

                yield f'msgid "{self.strip_key(term)}"\n'
                if len(forms) == 1:
                    yield f'msgstr "{forms[0]}"\n'
                else:
                    for i, form in forms.items():
                        yield f'msgstr[{i}] "{form}"\n'
                yield '\n'


    def write_one_po_file(self, lang):
        if not self.path_for_lang(lang).exists():
            return

        with open(path.join(self.path_for_lang(lang), "django.po"), "w") as outfile:
            outfile.write(PoFileHeader.get_header_for_lang(lang))
            for string in self.generate_po_file(lang):
                outfile.write(string)
            # for str_txt in self.strings_txt:
            #     translations = str_txt.translations_by_language[lang]
            #     for key in str_txt.keys_in_order:
            #         if key.startswith("[["):
            #             outfile.write('####\n# {}\n####\n\n'.format(self.strip_key(key)))
            #             continue
            #         self.write_comment_and_tag(str_txt, key, outfile)
            #         if key in translations:
            #             outfile.write("msgid \"{}\"\n".format(self.strip_key(key).replace('"', r'\"')))
            #             outfile.write("msgstr \"{}\"\n\n".format(translations[key].replace('"', r'\"')))


    def create_locale_folders(self):
        paths = map(self.path_for_lang, self.all_langs)
        for fpath, lang in zip(paths, self.all_langs):
            if not path.exists(fpath):
                self.warnings.append(
"""No localization directory exists for language: {lang}. Please, run

        python manage.py makemessages -l {lang}

to create the corresponding folder structure. Please check if there are any special
headers added in the generated .po file and add them to this script.\n
***  FOR NOW THIS LANGUAGE ({lang}) WILL BE IGNORED  ***""".format(lang=lang)
                )
                # makedirs(fpath)


class Command(BaseCommand):
    help = "Generate .po files from the strings.txt file"

    def __init__(self):
        super(BaseCommand, self).__init__()
        self.locale_paths = list(map(Path, settings.LOCALE_PATHS))


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
"Report-Msgid-Bugs-To: dtv@maps.me\\n"
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
