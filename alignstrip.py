import argparse
import json
import shlex
import subprocess as sp

import audiolabel

parser = argparse.ArgumentParser()
parser.add_argument('textgrid')
parser.add_argument('wav')
parser.add_argument('outdir')

args = parser.parse_args()

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
        start = label.t1,
        end = label.t2,
        text = label.text,
        duration = label.t2-label.t1,
        amplitude = float(lines[7].split()[2])
    ))
raw_text = json.dumps(result, indent=2)
open('{}/data.json'.format(args.outdir), 'w').write(raw_text)
