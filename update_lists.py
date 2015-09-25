#!/usr/bin/env python
# Retrieve words list from:
# https://github.com/shutterstock/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words
from argparse import ArgumentParser
from collections import defaultdict
import os
import re

LANG_FILENAME = re.compile(r'[a-z]{2,3}')
RUST_FILENAME = 'src/words.rs'

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def get_langs(langs_dir):
    filename_filter = lambda filename: LANG_FILENAME.match(
        filename) is not None
    return [filename for filename in os.listdir(langs_dir) if filename_filter(filename)]

def get_words(filename):
    with open(filename) as f:
        return [word.strip() for word in f if len(word.strip()) > 0]

# Main


def main(args):
    langs = get_langs(args.lists_dir)

    words = defaultdict(list)

    for lang in langs:
        lang_filename = os.path.join(args.lists_dir, lang)
        words[lang] = get_words(lang_filename)

    with open(RUST_FILENAME, 'w+') as f:
        f.write('#[derive(Clone, Copy)]\n')
        f.write('#[repr(u8)]\n')
        f.write('pub enum Lang { %s }\n' % (', '.join([lang.upper() for lang in sorted(langs)])))

        for (lang, lang_words) in sorted(words.items(), key=lambda item: item[0]):
            f.write('\n')
            f.write('static WORDS_%s: [&\'static str; %d] = [\n' % (lang.upper(), len(lang_words)))
            for chunk in chunks(lang_words, 10):
                f.write('    %s,\n' % (', '.join(list(map(lambda word: '"%s"' % (word), chunk)))))
            f.write('];\n')

        f.write('\n')
        f.write('pub static WORDS: [&\'static [&\'static str]; %d] = [%s];\n' % (len(words), ', '.join(['&WORDS_%s' % (lang.upper()) for lang in sorted(langs)])))

# Entry
parser = ArgumentParser()
parser.add_argument('lists_dir')


if __name__ == '__main__':
    main(parser.parse_args())
