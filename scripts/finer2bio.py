#!/usr/bin/env python3

import sys
import re

from logging import warning


# See https://github.com/Traubert/FiNer-rules/blob/master/finer-readme.md
TYPE_MAP = {
    'EnamexLocPpl': 'LOC',
    'EnamexPrsHum': 'PER',
    'TimexTmeDat': 'DATE',
    'TimexTmeHrm': None,    # Clock
    'EnamexOrgCrp': 'ORG',
    'EnamexLocGpl': 'LOC',
    'EnamexProXxx': 'PRO',
    'EnamexPrsTit': None,    # Title
    'EnamexOrgTvr': 'ORG',
    'EnamexOrgClt': 'ORG',
    'EnamexOrgAth': 'ORG',
    'EnamexOrgEdu': 'ORG',
    'EnamexOrgPlt': 'ORG',
    'EnamexLocFnc': 'LOC',
    'EnamexEvtXxx': 'EVENT',
    'EnamexLocStr': 'LOC',
    'EnamexPrsMyt': 'PER',
    'EnamexPrsAnm': 'PER',
    'EnamexOrgFin': 'ORG',
    'EnamexLocAst': 'LOC',
    'NumexMsrXxx': None,    # Units
    'NumexMsrCur': None,    # Money
}


class FormatError(Exception):
    pass


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('data', nargs='+')
    return ap


def resolve_multiple_tags(tag):
    m = re.match(r'^(</?[a-zA-Z]+/?>)(?:</?[a-zA-Z]+/?>)+$', tag)
    if m:
        first = m.group(1)
        warning('multiple tags "{}", treating as "{}"'.format(tag, first))
        return first
    else:
        return tag


def is_start_tag(tag):
    return re.match(r'^<[a-zA-Z]+>$', tag)


def is_end_tag(tag):
    return re.match(r'^</[a-zA-Z]+>$', tag)


def is_empty_tag(tag):
    return re.match(r'^<[a-zA-Z]+/>$', tag)


def get_tag_type(tag):
    m = re.match(r'</?([a-zA-Z]+)/?>$', tag)
    if not m:
        raise FormatError('tag "{}"'.format(tag))
    else:
        type_ = m.group(1)
        if type_ not in TYPE_MAP:
            print('warning: unknown type {}'.format(type_), file=sys.stderr)
            return type_
        else:
            return TYPE_MAP[type_]


def make_bio(prefix, type_):
    if prefix == 'O' or type_ is None:
        return 'O'
    else:
        return '{}-{}'.format(prefix, type_)


def process_sentence(sentence, options):
    if not sentence:
        return
    current = None
    for token, tag in sentence:
        if tag:
            tag = resolve_multiple_tags(tag)
        if not tag:
            if current is None:
                bio = 'O'
            else:
                bio = 'I-{}'.format(current)
        elif is_start_tag(tag):
            if current is not None:
                raise FormatError('nested')
            current = get_tag_type(tag)
            bio = make_bio('B', current)
        elif is_end_tag(tag):
            if current != get_tag_type(tag):
                raise FormatError('mismatch')
            bio = make_bio('I', current)
            current = None
        elif is_empty_tag(tag):
            bio = make_bio('B', get_tag_type(tag))
            current = None
        else:
            raise FormatError('tag "{}"'.format(tag))
        print('{}\t{}'.format(token, bio))
    print()


def process(fn, options):
    sentence = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if not l or l.isspace():
                process_sentence(sentence, options)
                sentence = []
            else:
                fields = l.split('\t')
                if len(fields) != 2:
                    raise FormatError('line {} in {}: {}'.format(
                            ln, fn, l))
                sentence.append(fields)
    process_sentence(sentence, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.data:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
