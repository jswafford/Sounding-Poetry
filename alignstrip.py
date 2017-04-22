import argparse
import json
import shlex
import subprocess as sp

# audiolabel: https://github.com/rsprouse/audiolabel

import audiolabel

# uses argparse module to parse command line arguments of the form 'python alignstrip.py textgrid wav outdir'


parser = argparse.ArgumentParser()
parser.add_argument('textgrid')
parser.add_argument('wav')
parser.add_argument('outdir')

# stores parsed values of command line arguments in variable args
args = parser.parse_args()

# create LabelManager from file and file type
data = audiolabel.LabelManager(from_file=args.textgrid, from_type="praat")

# stores 'word' tier (rather than syllable tier) from audio file in an empty list
tier = data.tier('word')
result = []

# to make excerpts split by word
for i, label in enumerate(tier):
    # creates new audio file for each word numbered sequentially
    filename = '{}/excerpts/excerpt{}.wav'.format(args.outdir, i)
    #uses shlex to split the string for the command line (to run to split the audio file)
    trimcommand = shlex.split('sox {} {} trim {} ={}'.format(args.wav, filename, label.t1, label.t2))
    #uses shlex to split the string for the command line (to compute amplitude)
    ampcommand = shlex.split('sox {} -n stat'.format(filename))
    #uses subprocess to run trimcommand on the command line
    trim = sp.Popen(trimcommand, stderr=sp.PIPE)
    trim.wait()
    #uses subprocess to run ampcommand on the command line
    amplitude = sp.Popen(ampcommand, stderr=sp.PIPE)
    #writes amplitude to stderr, splits it out into different lines, and stores it
    lines = amplitude.stderr.read().splitlines()
    
# stores start, end, text, duration, and amplitude for each word in a dictionarh
    result.append(dict(
        start = label.t1,
        end = label.t2,
        text = label.text,
        duration = label.t2-label.t1,
        amplitude = float(lines[7].split()[2])
    ))
# stores result in json string    
raw_text = json.dumps(result, indent=2)

# writes to json file
open('{}/data.json'.format(args.outdir), 'w').write(raw_text)
