import argparse
import json
import shlex
import subprocess as sp

# audiolabel - not installable via pip?

import audiolabel

TEXTGRID = "NEED_DEFAULT_VALUE_HERE"
WAV = "NEED_DEFAULT_VALUE_HERE"
OUTDIR = "NEED_DEFAULT_VALUE_HERE"

# TODO: document arg parsing here.

# adds arguments for parsing


def parse_args(argv=None):
    """Parses the command line.
    If no arguments are given, it will default to a given set of commands."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--textgrid', dest='textgrid', action='store',
                        default=TEXTGRID,
                        help='Describes what the argument does.'
                        ' Default = {}.'.format(TEXTGRID))
    parser.add_argument('-w', '--wav', dest='wav',
                        default=WAV,
                        help='Describes what the argument does.'
                        ' Default = {}'.format(WAV))
    parser.add_argument('-o', '--outdir', dest='outdir',
                        action='store', default=OUTDIR,
                        help='Describes what the argument does. Default = {}')
    return parser.parse_args(argv)


def main():
    """The main function that is run when not imported in another module."""

    # parses arguments

    # when the thing runs using our functions,
    # delete following lines and uncomment
    # the last line to use our own parsing function.
    parser = argparse.ArgumentParser()
    parser.add_argument('textgrid')
    parser.add_argument('wav')
    parser.add_argument('outdir')
    args = parser.parse_args()
    # args = parse_args()

    data = audiolabel.LabelManager(from_file=args.textgrid, from_type="praat")
    tier = data.tier('word')
    result = []

    for i, label in enumerate(tier):
        # to make excerpts split by word
        filename = '{}/excerpts/excerpt{}.wav'.format(args.outdir, i)
        trimcommand = shlex.split('sox {} {} trim {} ={}'.format(args.wav, filename, label.t1, label.t2))
        ampcommand = shlex.split('sox {} -n stat'.format(filename))
        trim = sp.Popen(trimcommand, stderr=sp.PIPE)
        trim.wait()
        amplitude = sp.Popen(ampcommand, stderr=sp.PIPE)
        lines = amplitude.stderr.read().splitlines()

        result.append(dict(
            start=label.t1,
            end=label.t2,
            text=label.text,
            duration=label.t2-label.t1,
            amplitude=float(lines[7].split()[2])
        ))
    raw_text = json.dumps(result, indent=2)
    open('{}/data.json'.format(args.outdir), 'w').write(raw_text)
