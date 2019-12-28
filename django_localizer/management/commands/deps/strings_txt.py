#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
from collections import namedtuple, defaultdict
import re
from pathlib import Path
from typing import Tuple, Dict, Set, List

TransAndKey = namedtuple("TransAndKey", "translation, key")

TRANSLATION = re.compile(r"(.*)\s*=\s*.*$", re.S | re.MULTILINE)
MANY_DOTS = re.compile(r"\.{4,}")
SPACE_PUNCTUATION = re.compile(r"\s[.,?!:;]")
PLACEHOLDERS = re.compile(r"(%\(\d*\w+\)[ds])")

LANG_ORDER = ["en", "en-GB", "ru"]


class line_reader:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        self.strings_txt = open(self.file_path)
        return self._lines()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.strings_txt.close()

    def _lines(self):
        for string in self.strings_txt:
            string = string.strip()
            if not string:
                continue

            yield Line(string)


class Line(str):
    def is_section(self) -> bool:
        return self.startswith('[[')


    def is_key(self) -> bool:
        return self.startswith('[')


    def is_translation(self) -> bool:
        return bool(TRANSLATION.match(self))


    def lang_and_translation(self) -> Tuple[str, str]:
        lang, _, tran = self.partition('=')
        tran = self._process_translation(tran)
        return lang, tran


    def _process_translation(self, translation):
        if MANY_DOTS.search(translation):
            print(f'WARNING: 4 or more dots in the string: {self}')
        return translation.strip().replace("...", "…")

Key = str
Lang = str
Translation = str

class StringsTxt:
    def __init__(self, strings_path):
        self.strings_path: Path = strings_path
        self.translations: Dict[Key, Dict[Lang, Translation]] = (
            defaultdict(lambda: defaultdict(str)))
        self.translations_by_language: Dict[Lang, Dict[Key, Translation]] = (
            defaultdict(dict))
        self.comments_and_tags = defaultdict(dict)
        self.all_langs: Set[str] = set()
        self.keys_in_order: List[Key] = []
        self.warnings = []

        self._read_file()
        self._populate_translations_by_langs()


    def _read_file(self):
        key = None
        with line_reader(self.strings_path) as lines:
            for line in lines:
                if line.is_section():
                    self.keys_in_order.append(line)
                    continue
                if line.is_key():
                    key = line
                    self._add_new_key(key)
                    continue
                if line.is_translation():
                    lang, tran = line.lang_and_translation()
                    if lang == 'comment' or lang == 'tags':
                        self.comments_and_tags[key][lang] = tran
                        continue

                    self.translations[key][lang] = tran
                    self.all_langs.add(lang)


    def _add_new_key(self, key):
        self.translations[key] = {}
        if key not in self.keys_in_order:
            self.keys_in_order.append(key)


    def _populate_translations_by_langs(self):
        for lang in self.all_langs:
            trans_for_lang = {}
            for key, tran in self.translations.items(): # (tran = dict<lang, translation>)
                if lang not in tran:
                    continue
                trans_for_lang[key] = tran[lang]
            self.translations_by_language[lang] = trans_for_lang


    def write_formatted(self, target_file=None, languages=None):
        before_block = ''
        if target_file is None:
            target_file = self.strings_path
        alphabetical_langs = sorted(list(self.all_langs - set(LANG_ORDER)))
        with open(target_file, 'w') as outfile:
            for key in self.keys_in_order:
                if not key:
                    continue
                if key in self.translations:
                    tran = self.translations[key]
                else:
                    if key.startswith('[['):
                        outfile.write(f'{before_block}{key}\n')
                        before_block = '\n'
                    continue

                outfile.write(f'{before_block}  {key}\n')
                before_block = '\n'

                if key in self.comments_and_tags:
                    for k, v in self.comments_and_tags[key].items():
                        outfile.write(f'    {k} = {v}\n')
                self._write_translations_for_langs(LANG_ORDER, tran, outfile, only_langs=languages)
                self._write_translations_for_langs(alphabetical_langs, tran, outfile, only_langs=languages)


    def _write_translations_for_langs(self, langs, tran, outfile, only_langs=None):
        langs_to_write = []

        if only_langs:
            for lang in only_langs:
                if lang in langs:
                    langs_to_write.append(lang)
        else:
            langs_to_write = langs

        for lang in langs_to_write:
            if lang in tran:
                outfile.write(f'    {lang} = {tran[lang]}\n')


    def _has_space_before_punctuation(self, lang_and_string):
        lang, string = lang_and_string
        if lang == "fr":
            return False
        if SPACE_PUNCTUATION.search(string):
            return True
        return False


    def find_spaces_before_punctuation(self):
        loc_warnings = []

        for key, lang_and_trans in self.translations.items():
            with_spaces = list(filter(
                self._has_space_before_punctuation, lang_and_trans.items()))

            if with_spaces:
                loc_warnings.append("{}:\n{}\n".format(
                    key,
                    "\n".join(map(lambda tup: "{}: {}".format(*tup), with_spaces))
                ))
        if loc_warnings:
            self.warnings.append(
                "These strings have spaces before punctuation marks:\n{}".format(
                    "\n".join(loc_warnings)
                )
            )


    def _check_placeholders_in_block(self, block_key):
        wrong_placeholders_strings = []
        key_placeholders = sorted(PLACEHOLDERS.findall(block_key))
        for lang, translation in self.translations[block_key].items():
            found = sorted(PLACEHOLDERS.findall(translation))
            if not key_placeholders == found: # must be sorted
                wrong_placeholders_strings.append("{} : {}".format(lang, translation))

        return wrong_placeholders_strings


    def find_wrong_paceholders(self):
        warnings = []

        for key, lang_and_trans in self.translations.items():
            for wr_placeholders in self._check_placeholders_in_block(key):
                warnings.append("{}\nEn: {}\n{}".format(
                    key, lang_and_trans["en"], wr_placeholders
                ))

        if warnings:
            self.warnings.append(
                "These strings have wrong numbers of placeholders in them:\n{}".format(
                    "\n".join(warnings)
                )
            )
