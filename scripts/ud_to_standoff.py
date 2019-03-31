#!/usr/bin/env python

# Generate text and standoff marking PROPN words and flat:name spans as name.

import os
import sys

from collections import namedtuple


Word = namedtuple('Word', 'id form lemma upos xpos feats head deprel deps misc')

Textbound = namedtuple('Textbound', 'id type start end text')


def group_into_sentences(conll_lines):
    sentences = []
    current = []
    for line in conll_lines:
        if not line or line.isspace():
            sentences.append(current)
            current = []
        elif line[0] == '#':
            pass
        else:
            current.append(line)
    return sentences


def name_spans(words):
    spans = set()
    for word in words:
        if word.deprel == 'flat:name':
            h, d = int(word.head), int(word.id)            
            spans.add((min(h,d), max(h,d)))
        if word.deps == '_':
            continue
        for dep in word.deps.split('|'):
            head, deprel = dep.split(':', 1)
            if deprel == 'flat:name':
                h, d = int(head), int(word.id)
                spans.add((min(h,d), max(h,d)))
    return spans


def name_tokens(words):
    spans = set()
    for word in words:
        if not word.id.isdigit():
            continue    # skip multiword tokens and empties
        if word.upos == 'PROPN':
            spans.add((int(word.id), int(word.id)))
    return spans


def remove_nested(spans):
    nonnested = set()
    for s in spans:
        if not any (n for n in spans if ((n[0] < s[0] and n[1] >= s[1]) or
                                         (n[0] <= s[0] and n[1] > s[1]))):
            nonnested.add(s)
    return nonnested


def word_offsets(words, base_offset):
    offsets = {}
    current = base_offset
    for word in words:
        if not word.id.isdigit():
            continue    # skip multiword tokens and empties
        offsets[int(word.id)] = (current, current+len(word.form))
        current += len(word.form)+1
    return offsets


def span_text(words, start_token, end_token):
    spanned = [
        w for w in words
        if w.id.isdigit() and start_token <= int(w.id) <= end_token
    ]
    return ' '.join(w.form for w in spanned)

    
def main(argv):
    if len(argv) != 2:
        print('Usage: {} FILE'.format(os.path.basename(__file__)),
              file=sys.stderr)
        return 1

    with open(argv[1]) as f:
        lines = [l.rstrip('\n') for l in f]

    sentences = group_into_sentences(lines)

    doc_text, textbounds = '', []
    for sentence in sentences:
        words = [Word(*w.split('\t')) for w in sentence]
        names = remove_nested(name_spans(words) | name_tokens(words))
        offsets = word_offsets(words, len(doc_text))
        for start_token, end_token in sorted(names):
            textbounds.append(Textbound(
                'T{}'.format(len(textbounds)+1), 'name',
                offsets[start_token][0], offsets[end_token][1],
                span_text(words, start_token, end_token)
            ))
        doc_text += ' '.join(
            w.form for w in words
            if w.id.isdigit()
        ) + '\n'

    root, _ = os.path.splitext(os.path.basename(argv[1]))
    text_fn, ann_fn = root + '.txt', root + '.ann'

    with open(text_fn, 'wt') as out:
        out.write(doc_text)
    with open(ann_fn, 'wt') as out:
        for t in textbounds:
            print('{}\t{} {} {}\t{}'.format(*t), file=out)
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
