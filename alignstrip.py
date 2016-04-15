import argparse
import json
import shlex
import subprocess as sp
import sys

# audiolabel - not installable via pip?

import audiolabel

# default values for parsing if none are given as arguments.

TEXTGRID = "NEED_DEFAULT_VALUE_HERE"
WAV = "NEED_DEFAULT_VALUE_HERE"
OUTDIR = "NEED_DEFAULT_VALUE_HERE"

# TODO: document arg parsing here.


def parse_args(argv=None):
    """Parses the command line input.
    If no arguments are given, it will default to a given set of commands."""

    argv = sys.argv[1:] if argv is None else argv
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

    # old way of parsing
    # parser = argparse.ArgumentParser()
    # parser.add_argument('textgrid')
    # parser.add_argument('wav')
    # parser.add_argument('outdir')
    # args = parser.parse_args()

    # parses arguments
    args = parse_args()

    data = audiolabel.LabelManager(from_file=args.textgrid, from_type="praat")
    tier = data.tier('word')
    result = []

    for i, label in enumerate(tier):
        # to make excerpts split by word
        filename = '{}/excerpts/excerpt{}.wav'.format(args.outdir, i)

        # preps sox (cli) 'trim' command to split
        # the file into pieces based on the words
        trimcommand = shlex.split('sox {} {} trim {} ={}'.format(
                        args.wav, filename, label.t1, label.t2))

        # preps sox (cli) 'stat' command to pull
        # the peak amplitude for the file.
        ampcommand = shlex.split('sox {} -n stat'.format(filename))

        # splits file into pieces. WHAT IS THE LOGIC HERE? NOT USED AGAIN?
        trim = sp.Popen(trimcommand, stderr=sp.PIPE)

        # waits until subprocess finishes
        trim.wait()

        # uses sox to generate peak amplitude
        amplitude = sp.Popen(ampcommand, stderr=sp.PIPE)

        # NOT SURE WHAT THIS DOES
        lines = amplitude.stderr.read().splitlines()

        # result is a series of dicts that contain
        # start and end times, text, duration, amplitudes.

        result.append(dict(
            start=label.t1,
            end=label.t2,
            text=label.text,
            duration=label.t2-label.t1,
            amplitude=float(lines[7].split()[2])
        ))

    raw_text = json.dumps(result, indent=2)
    open('{}/data.json'.format(args.outdir), 'w').write(raw_text)

if __name__ == '__main__':
    main()
