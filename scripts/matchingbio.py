#!/usr/bin/env python3

import sys


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('file1')
    ap.add_argument('file2')
    return ap


def process_streams(f1, f2, options):
    matched, total = 0, 0
    sent1, sent2 = [], []
    for ln, l1 in enumerate(f1, start=1):
        try:
            l2 = next(f2)
        except StopIteration:
            print('unexpected eof in {} at line {}'.format(f2.name, ln),
                  file=sys.stderr)
            return False
        l1, l2 = l1.rstrip('\n'), l2.rstrip('\n')
        if not l1 or l1.isspace():
            if l2 and not l2.isspace():
                print('desyncronized at line {}: "{}" vs "{}"'.format(ln, l1, l2),
                      file=sys.stderr)
                return False
            if sent1 == sent2:
                matched += 1
                for s in sent1:
                    print(s)
                print()
            total += 1
            sent1, sent2 = [], []
        else:
            if not l2 or l2.isspace():
                print('desyncronized at line {}: "{}" vs "{}"'.format(ln, l1, l2),
                      file=sys.stderr)
                return False
            sent1.append(l1)
            sent2.append(l2)
    try:
        l2 = next(f2)
        print('unexpected eof in {} at line {}'.format(f1.name, ln),
              file=sys.stderr)
        return False
    except StopIteration:
        pass
    print('done, found {}/{} matching sentences'.format(matched, total),
          file=sys.stderr)
    return True


def process(file1, file2, options):
    with open(file1) as f1:
        with open(file2) as f2:
            return process_streams(f1, f2, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    process(args.file1, args.file2, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
