#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
from collections import namedtuple, defaultdict
import re

TransAndKey = namedtuple("TransAndKey", "translation, key")

TRANSLATION = re.compile(r"(.*)\s*=\s*.*$", re.S | re.MULTILINE)
MANY_DOTS = re.compile(r"\.{4,}")
SPACE_PUNCTUATION = re.compile(r"\s[.,?!:;]")
PLACEHOLDERS = re.compile(r"(%\(\d*\w+\)[ds])")

LANG_ORDER = ["en", "en-GB", "ru"]


class StringsTxt:

    def __init__(self, strings_path):
        self.strings_path = strings_path
        self.translations = defaultdict(lambda: defaultdict(str)) # dict<key, dict<lang, translation>>
        self.translations_by_language = defaultdict(dict) # dict<lang, dict<key, translation>>
        self.comments_and_tags = defaultdict(dict)
        self.all_langs = set()
        self.keys_in_order = []
        self.warnings = []

        self._read_file()
        self._populate_translations_by_langs()


    def _read_file(self):
        with open(self.strings_path) as strings:
            for line in strings:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("[["):
                    self.keys_in_order.append(line)
                    continue
                if line.startswith("["):
                    # if line in self.translations:
                    #     print("Duplicate key {}".format(line))
                    #     continue
                    self.translations[line] = {}
                    current_key = line
                    if current_key not in self.keys_in_order:
                        self.keys_in_order.append(current_key)
                    continue

                if TRANSLATION.match(line):
                    lang, tran = self._parse_lang_and_translation(line)

                    if lang == "comment" or lang == "tags":
                        self.comments_and_tags[current_key][lang] = tran
                        continue

                    self.translations[current_key][lang] = tran
                    self.all_langs.add(lang)


    def _parse_lang_and_translation(self, line):
        ret = tuple(map(self._process_string, line.split(" = ", 1)))
        assert len(ret) == 2, "Couldn't parse the line: {0}".format(line)
        return ret


    def _process_string(self, string):
        if MANY_DOTS.search(string):
            print("WARNING: 4 or more dots in the string: {0}".format(string))
        return str.strip(string).replace("...", "…")


    def _populate_translations_by_langs(self):
        for lang in self.all_langs:
            trans_for_lang = {}
            for key, tran in self.translations.items(): # (tran = dict<lang, translation>)
                if lang not in tran:
                    continue
                trans_for_lang[key] = tran[lang]
            self.translations_by_language[lang] = trans_for_lang


    def write_formatted(self, target_file=None, languages=None):
        before_block = ""
        if target_file is None:
            target_file = self.strings_path
        non_itunes_langs = sorted(list(self.all_langs - set(LANG_ORDER)))
        with open(target_file, "w") as outfile:
            for key in self.keys_in_order:
                if not key:
                    continue
                if key in self.translations:
                    tran = self.translations[key]
                else:
                    if key.startswith("[["):
                        outfile.write("{0}{1}\n".format(before_block, key))
                        before_block = "\n"
                    continue

                outfile.write("{0}  {1}\n".format(before_block, key))
                before_block = "\n"

                if key in self.comments_and_tags:
                    for k, v in self.comments_and_tags[key].items():
                        outfile.write("    {0} = {1}\n".format(k, v))
                self._write_translations_for_langs(LANG_ORDER, tran, outfile, only_langs=languages)
                self._write_translations_for_langs(non_itunes_langs, tran, outfile, only_langs=languages)


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
                outfile.write("    {0} = {1}\n".format(lang, tran[lang]))


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
